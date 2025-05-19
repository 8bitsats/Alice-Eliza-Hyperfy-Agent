import dotenv from 'dotenv'
dotenv.config()

import 'ses'

globalThis.self = globalThis; 

    // Mock window minimally
    globalThis.window = globalThis.window || globalThis; 
    
import { performance } from 'perf_hooks' // Node.js performance hooks
import * as THREE from 'three' // <-- Add THREE import
import fs from 'fs/promises' // <-- Add FS import
import path from 'path'      // <-- Add Path import
import { createClientWorld, loadNodePhysX, storage, extendThreePhysX, geometryToPxMesh } from '../../build/core.js'
import crypto from 'crypto'
import { AgentLoader } from './AgentLoader.js'
import { AgentControls } from './AgentControls.js'

export async function hashFileBuffer(buffer) {
  // Ensure crypto.subtle is available
  if (!crypto.subtle || typeof crypto.subtle.digest !== 'function') {
    throw new Error("crypto.subtle.digest is not available.");
  }
  const hashBuf = await crypto.subtle.digest('SHA-256', buffer);
  const hash = Array.from(new Uint8Array(hashBuf))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  return hash;
}


// --- Configuration ---
const WS_URL = process.env.WS_URL || 'wss://chill.hyperfy.xyz/ws'
const TICK_RATE = 50 // Hz (how often world.tick runs)
const MOVE_INTERVAL = 1000 // ms (how often the agent changes direction)
const CHAT_INTERVAL = 5000 // ms (how often the agent sends a chat message) - Updated
const LOG_INTERVAL = 1000 // ms (how often to log user data)
const ENTITY_LOG_INTERVAL = 5000 // ms (how often to log all entities) <-- Add Entity Log Interval
const LOCAL_AVATAR_PATH = './avatar.vrm' // <-- Define local avatar path
// ---------------------

let tickIntervalId = null
let moveIntervalId = null
let chatIntervalId = null
let logIntervalId = null // <-- Add ID for log interval
let soundIntervalId = null // <-- Add ID for sound interval
let processedMsgIds = new Set() // <-- ADD THIS
let entityLogIntervalId = null // <-- Add Entity Log Interval ID
let playerNamesMap = new Map() // <-- 1. Declare the map here
let appearanceIntervalId = null // <-- Add ID for appearance polling
let appearanceSet = false // <-- Add appearance set flag

const AGENT_NAME = 'Agent'
// const AGENT_AVATAR_URL = 'https://github.com/elizaOS/brandkit/raw/refs/heads/main/avatars/eliza_hat.vrm' // No longer primary
// Expose the map on the global world object so ClientNetwork can access it
// (Do this *before* creating the world)
if (typeof global !== 'undefined') {
  global.playerNamesMap = playerNamesMap;
} else if (typeof window !== 'undefined') {
  window.playerNamesMap = playerNamesMap;
}

let world
if (typeof window !== 'undefined') {
  // Browser environment
  window.world = world
  window.THREE = THREE
  window.env = process.env
} else if (typeof global !== 'undefined') {
  // Node.js environment
  global.world = world
  global.THREE = THREE
  global.env = process.env
}

// Determine __dirname in ES Module scope
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runAgent() {
  console.log(`Agent connecting to ${WS_URL}...`)

  // Asynchronously get the stored auth token BEFORE initializing the world
  console.log('Attempting to retrieve stored authToken...')
  const initialAuthToken = await storage.get('authToken')
  console.log(`Retrieved initialAuthToken: ${initialAuthToken}`)

  function registerSystem(key, SystemClass, proxyHandler = null) {
    const system = new SystemClass(world)
    world[key] = proxyHandler ? new Proxy(system, proxyHandler) : system
    world.systems.push(system) // Push the original system for the update loop
    return system
  }

  // Specify 'node' environment to load only necessary core systems
  world = createClientWorld({
    controls: AgentControls,
    loader: AgentLoader
  })

  // Attach the map reference to the world instance
  world.playerNamesMap = playerNamesMap;
  
  // --- Define listener functions ---
  // REMOVED entityModifiedListener as it's handled directly in ClientNetwork now

  // Listener for entity ADDED 
  const entityAddedListener = (entity) => {
      // Check if it's a player and has a name in its initial data
      if (entity?.data?.type === 'player' && entity.data.name) {
          // Check if name already exists from a rapid modify before add event
          if (!playerNamesMap.has(entity.id)) { 
              console.log(`[Name Map Add] Setting initial name for ID ${entity.id}: '${entity.data.name}'`);
              playerNamesMap.set(entity.id, entity.data.name); // Add to map
          }
      }
  };

  const entityRemovedListener = (entityId) => {
      if (playerNamesMap.has(entityId)) {
          console.log(`[Name Map Update] Removing name for ID ${entityId}`);
          playerNamesMap.delete(entityId); // Remove from map
      }
  };
  // -----------------------------------------------------------------

  // Mock viewport/UI elements needed by some client systems
  const mockElement = {
    appendChild: () => {},
    removeChild: () => {},
    offsetWidth: 1920,
    offsetHeight: 1080,
    addEventListener: () => {},
    removeEventListener: () => {},
    style: {},
  }

  const config = {
    wsUrl: WS_URL,
    loadPhysX: loadNodePhysX,
    viewport: mockElement, // Mock
    ui: mockElement, // Mock
    initialAuthToken: initialAuthToken, // <-- Pass the retrieved token here
  }

  try {
    // --- Load PhysX FIRST ---
    // world.init calls config.loadPhysX internally if physics system exists
    // We need the result *before* fully initializing the world systems if we call extend manually
    console.log("[Agent Setup] Explicitly loading PhysX via loadNodePhysX...");
    await loadNodePhysX(); // Ensure PhysX is loaded and PHYSX is global
    console.log("[Agent Setup] PhysX loaded, calling extendThreePhysX...");
    extendThreePhysX(); // <-- Call the extension function
    console.log("[Agent Setup] extendThreePhysX called.");
    // -------------------------

    // Now initialize the world systems, which will use the loaded PhysX
    await world.init(config)
    console.log('World initialized...')

    // --- Verify Physics System ---
    if (!world.physics?.physics || !world.physics?.scene || !world.physics?.cooking) { /* ... error ... */ }
    else { console.log("[Agent Setup] Physics system seems initialized."); }
    // --------------------------

    // --- Load Environment Geometry ---
    console.log("[Agent Setup] Attempting to load environment model...");
    const envModelUrl = world.settings?.model?.url;
    if (envModelUrl) {
       try {
           const envGltf = await world.loader.load('model', envModelUrl);
           console.log(`[Agent Setup] Environment model loaded: ${envModelUrl}`);
           await setupStaticPhysicsGeometry(world, envGltf); // Call the setup function
       } catch (error) {
            console.error(`[Agent Setup] Failed to load or process environment model ${envModelUrl}:`, error);
       }
    } else {
         console.warn("[Agent Setup] No environment model URL found in world settings.");
    }
    // -------------------------------

    // --- 3. Add listeners after world is ready (only Added/Removed needed now) ---
    if (world?.entities) { 
        console.log('[Agent Setup] Attaching entityAdded/Removed listeners to world.entities...');
        world.entities.on('entityAdded', entityAddedListener);
        world.entities.on('entityRemoved', entityRemovedListener);
    }
    // -----------------------------------------------------------------

    // Start the simulation loop IMMEDIATELY after init
    startSimulation()

    // Start the other functions - they will wait internally for the player
    startRandomMovement()
    startChatSubscription()
    startRandomChatting()
    startUserDataLogging()
    startEntityLogging() // <-- Call new function
    // startRandomSoundPlayback() // <-- Commented out

    // Keep listening for disconnect/kick
    world.on('disconnect', reason => {
      console.log('Agent Disconnected.', reason)
      stopAgent()
    })
    world.on('kick', code => {
      console.log('Agent Kicked:', code)
      stopAgent()
    })

    // Start appearance polling
    startAppearancePolling()
  } catch (error) {
    console.error('Failed to initialize agent:', error)
    stopAgent()
  }
}

function startSimulation() {
  if (tickIntervalId) clearInterval(tickIntervalId)
  const tickIntervalMs = 1000 / TICK_RATE
  let lastTickTime = performance.now()

  function tickLoop() {
    const now = performance.now()
    // console.log(`[Agent tickLoop] Running at time: ${now}`); // <-- Log loop entry
    try {
      world.tick(now)
      // console.log(`[Agent tickLoop] world.tick completed.`); // <-- Log after tick (if no error)
    } catch (e) {
      console.error('[Agent tickLoop] Error during world.tick:', e) // <-- Catch errors
      // Optionally stop the loop on error:
      // if (tickIntervalId) clearTimeout(tickIntervalId);
      // stopAgent();
      // return;
    }
    lastTickTime = now
    // Schedule next tick precisely
    const elapsed = performance.now() - now
    const delay = Math.max(0, tickIntervalMs - elapsed)
    // console.log(`[Agent tickLoop] Scheduling next tick with delay: ${delay.toFixed(2)}ms`); // <-- Log scheduling
    tickIntervalId = setTimeout(tickLoop, delay)
  }

  console.log(`[Agent startSimulation] Starting simulation tick at ${TICK_RATE}Hz.`) // <-- Log start func
  tickLoop() // Start the first tick
}

function startRandomMovement() {
  if (moveIntervalId) clearInterval(moveIntervalId)
  console.log(`[Agent startRandomMovement] Initializing interval every ${MOVE_INTERVAL}ms.`)

  // Store the currently active key to easily turn it off
  let currentKey = null

  moveIntervalId = setInterval(() => {
    // --> WAIT for player entity <--
    if (!world || !world.entities?.player) {
      // console.log("[Agent startRandomMovement] Waiting for player entity...");
      return
    }
    const controls = world.controls // Get controls inside interval once player exists
    if (!controls || typeof controls.setKey !== 'function') {
      console.error('[Agent startRandomMovement] AgentControls system not found or missing setKey method!')
      clearInterval(moveIntervalId) // Stop trying if controls are wrong
      return
    }

    // Turn off the previously active key (if any)
    if (currentKey) {
      controls.setKey(currentKey, false)
      currentKey = null
    }
    // Reset shift key
    controls.setKey('shiftLeft', false)

    const direction = Math.floor(Math.random() * 5) // 0:W, 1:A, 2:S, 3:D, 4:Stop
    let moveKey = null

    switch (direction) {
      case 0:
        moveKey = 'keyW'
        console.log('Agent moving: FORWARD')
        break
      case 1:
        moveKey = 'keyA'
        console.log('Agent moving: LEFT')
        break
      case 2:
        moveKey = 'keyS'
        console.log('Agent moving: BACKWARD')
        break
      case 3:
        moveKey = 'keyD'
        console.log('Agent moving: RIGHT')
        break
      case 4:
        /* Stop */ console.log('Agent moving: STOP')
        break
    }

    // Set the new key state
    if (moveKey) {
      controls.setKey(moveKey, true)
      currentKey = moveKey // Remember which key is active
    }

    // Maybe randomly run sometimes?
    if (moveKey && Math.random() < 0.2) {
      controls.setKey('shiftLeft', true)
    }
  }, MOVE_INTERVAL)
}

function startChatSubscription() {
  if (!world || !world.chat) {
    console.error('Cannot subscribe to chat: World or Chat system not available.')
    return
  }
  console.log('[Agent startChatSubscription] Initializing chat subscription...')
  // Pre-populate processed IDs with existing messages
  world.chat.msgs?.forEach(msg => processedMsgIds.add(msg.id));
  console.log(`[Agent startChatSubscription] Initial processed message IDs: ${processedMsgIds.size}`);

  world.chat.subscribe(msgs => {
    // --> WAIT for player entity (ensures world/chat exist too) <--
    if (!world || !world.chat || !world.entities?.player) return
    
    const agentPlayerId = world.entities.player.id; // Get agent's ID
    const agentPlayerName = world.entities.player.data.name || 'Agent'; // Get agent's name

    const newMessagesFound = []; // <-- Temporary list for new messages

    // --- Step 1: Identify new messages and update processed set --- 
    msgs.forEach(msg => {
      // Check if we've already processed this message ID
      if (msg && msg.id && !processedMsgIds.has(msg.id)) { // Add checks for msg and msg.id
        newMessagesFound.push(msg); // Add the full message object
        processedMsgIds.add(msg.id); // Mark ID as processed *immediately*
      }
    });
    // -----------------------------------------------------------

    // --- Step 2: Process only the newly found messages --- 
    if (newMessagesFound.length > 0) {
      console.log(`[Agent Chat] Found ${newMessagesFound.length} new messages to process.`);
      newMessagesFound.forEach(msg => {
        const senderName = msg.from || 'System'
        const messageBody = msg.body || ''
        console.log(`[Agent Chat Received] From: ${senderName}, ID: ${msg.id}, Body: "${messageBody}"`);

        // Respond only to messages not from the agent itself
        if (msg.fromId !== agentPlayerId) {
          const response = `Responding to ${senderName}: "${messageBody}"`;
          console.log(`[Agent Chat Sending] Body: "${response}"`);
          world.chat.add({ 
            body: response, 
            fromId: agentPlayerId, 
            from: agentPlayerName 
            // Let Chat system assign the new ID
          }, true); // <-- Add true for broadcast
          // Note: Recording trigger logic removed for clarity, can be re-added here if needed
        }
        // No need to add to processedMsgIds here, already done in Step 1
      });
    }
    // -------------------------------------------------------

  })
}

function startRandomChatting() {
  if (chatIntervalId) clearInterval(chatIntervalId)
  console.log(`[Agent startRandomChatting] Initializing interval every ${CHAT_INTERVAL}ms.`)

  const messagesToSend = ['hello', 'hi', 'hey']

  chatIntervalId = setInterval(() => {
    // --> WAIT for player entity <--
    if (!world || !world.chat || !world.entities?.player) {
      // console.log("[Agent startRandomChatting] Waiting for player/chat...");
      return
    }
    
    const agentPlayerId = world.entities.player.id; // Get agent's ID
    const agentPlayerName = world.entities.player.data.name || 'Agent'; // Get agent's name

    const randomMessage = messagesToSend[Math.floor(Math.random() * messagesToSend.length)];
    console.log(`[Agent Chat Sending Random] Body: "${randomMessage}"`);
    // Send random message with agent's identity
    world.chat.add({ 
        body: randomMessage, 
        fromId: agentPlayerId, 
        from: agentPlayerName 
    }, true) // <-- Add true for broadcast

  }, CHAT_INTERVAL)
}

function startUserDataLogging() {
  if (logIntervalId) clearInterval(logIntervalId)
  console.log(`[Agent startUserDataLogging] Initializing interval every ${LOG_INTERVAL}ms.`)

  const baseForward = new THREE.Vector3(0, 0, -1)
  const currentDirection = new THREE.Vector3()

  logIntervalId = setInterval(() => {
    // --> WAIT for player entity <--
    if (!world || !world.entities?.player) {
      // console.log("[Agent startUserDataLogging] Waiting for player entity...");
      return
    }

  }, LOG_INTERVAL)
}

// --- Function to Log All Entities --- >
function startEntityLogging() {
  if (entityLogIntervalId) clearInterval(entityLogIntervalId);
  console.log(`[Agent startEntityLogging] Initializing interval every ${ENTITY_LOG_INTERVAL}ms.`);

  entityLogIntervalId = setInterval(() => {
    // Check if world and entities system are available
    if (!world || !world.entities || !world.entities.items) {
      console.log("[Agent Entity Logging] Waiting for world/entities...");
      return;
    }

    const entityCount = world.entities.items.size;
    const agentPlayerId = world?.entities?.player?.id; // Get current agent ID
    console.log(`
--- [Agent Entity Log - Time: ${world.time.toFixed(2)}s] --- (${entityCount} entities) ---`);

    try {
      world.entities.items.forEach((entity, id) => {
        const entityType = entity.data?.type || 'unknown';
        let namePart = ''; // Initialize as empty

        // 4. Get name from map ONLY for players (Use the map in logger)
        if (entityType === 'player') {
            const playerName = playerNamesMap.get(id); // Get name from map

            // Only add the name part if we actually found a name
            if (playerName) {
                namePart = `, Name: ${playerName}`; // Construct name part
                if (id === agentPlayerId) {
                    namePart += ' (You)'; // Add marker for self if name exists
                }
            }
             // If playerName is null/undefined, namePart remains empty, nothing added to log for name
        } else {
            // For non-players, use the entity's data.name if it exists
            if(entity.data?.name) {
                namePart = `, Name: ${entity.data.name}`;
            }
        }

        let logMessage = `  ID: ${id}, Type: ${entityType}${namePart}`; // Construct base log message


        // Check if the entity has a 'base' object for position/rotation
        if (entity.base) {
             const pos = entity.base.position;
             const rot = entity.base.quaternion;
             logMessage += `, Pos: (${pos.x.toFixed(2)}, ${pos.y.toFixed(2)}, ${pos.z.toFixed(2)})`;
             logMessage += `, Rot: (x:${rot.x.toFixed(2)}, y:${rot.y.toFixed(2)}, z:${rot.z.toFixed(2)}, w:${rot.w.toFixed(2)})`;
        } else if (entity.data?.position && entity.data?.quaternion) {
             // Fallback to data if base isn't available (might be less current)
             const pos = entity.data.position;
             const rot = entity.data.quaternion;
             // Ensure position/quaternion are arrays/objects that can be logged
             const posX = Array.isArray(pos) ? pos[0] : pos.x;
             const posY = Array.isArray(pos) ? pos[1] : pos.y;
             const posZ = Array.isArray(pos) ? pos[2] : pos.z;
             const rotX = Array.isArray(rot) ? rot[0] : rot.x;
             const rotY = Array.isArray(rot) ? rot[1] : rot.y;
             const rotZ = Array.isArray(rot) ? rot[2] : rot.z;
             const rotW = Array.isArray(rot) ? rot[3] : rot.w;
             logMessage += `, Pos (data): (${posX?.toFixed(2)}, ${posY?.toFixed(2)}, ${posZ?.toFixed(2)})`;
             logMessage += `, Rot (data): (x:${rotX?.toFixed(2)}, y:${rotY?.toFixed(2)}, z:${rotZ?.toFixed(2)}, w:${rotW?.toFixed(2)})`;
        }
        console.log(logMessage);
      });
      console.log(`--- [End Agent Entity Log] ---`);
    } catch (e) {
        console.error("[Agent Entity Logging] Error during entity iteration:", e);
    }

  }, ENTITY_LOG_INTERVAL);
}

// Make stopAgent async to await storage flush
async function stopAgent() {
  console.log('Stopping agent...')
  if (tickIntervalId) clearTimeout(tickIntervalId);
  if (moveIntervalId) clearInterval(moveIntervalId);
  if (chatIntervalId) clearInterval(chatIntervalId);
  if (logIntervalId) clearInterval(logIntervalId);
  if (entityLogIntervalId) clearInterval(entityLogIntervalId);
  if (appearanceIntervalId) clearInterval(appearanceIntervalId); appearanceIntervalId = null; // <-- Clear appearance interval
  tickIntervalId = null
  moveIntervalId = null
  chatIntervalId = null
  logIntervalId = null
  entityLogIntervalId = null;
  // soundIntervalId = null // <-- Commented out

  // --- Disconnect LiveKit --- >
  if (world?.livekit) {
    await world.livekit.disconnect();
    console.log('[Agent] LiveKit disconnected.')
  }
  // -------------------------- >

  // Flush storage writes before destroying world or exiting
  if (storage?.isNodeStorage) {
    // Check if it's NodeStorage using the flag
    try {
      await storage.flushWrites()
    } catch (e) {
      console.error('Error flushing storage writes during shutdown:', e)
    }
  } else if (storage) {
    console.log('[stopAgent] Storage is not NodeStorage, skipping flush.')
  }

  // --- 5. Remove listeners and clear map before destroying world ---
  if (world?.entities) { 
      console.log("[Agent Cleanup] Removing entity listeners from world.entities...");
      world.entities.off('entityAdded', entityAddedListener);
      world.entities.off('entityRemoved', entityRemovedListener);
  }
  // --------------------------------------------------------------

  world?.destroy()
  world = null
  console.log('Agent stopped and resources released.');
  // Removed process.exit(0) to allow potential reconnection
}

// Handle graceful shutdown - make handlers async
process.on('SIGINT', async () => {
  console.log('SIGINT received.')
  await stopAgent()
})
process.on('SIGTERM', async () => {
  console.log('SIGTERM received.')
  await stopAgent()
})

// --- Add Helper Function to Set Appearance --- >
// UNCOMMENTED setAgentAppearance function
function setAgentAppearance(targetWorld, name, avatarUrl) {
    // Use world.network.id directly
    const networkId = targetWorld?.network?.id;
    if (!networkId) { 
      console.error("[setAgentAppearance] world.network.id not available yet.");
      return; 
    }

    // Optional: Check if player entity exists for logging, but don't rely on its id
    if (!targetWorld.entities?.player) {
        console.warn("[setAgentAppearance] world.entities.player does not exist yet, but proceeding with network ID.");
    }

    const playerId = networkId; // Use the network ID as the player ID

    console.log(`[Agent Setup] Setting name to "${name}" and avatar to "${avatarUrl}" using network ID ${playerId}`);
    
    // Send name update using the network ID
    // targetWorld.network.send('entityModify', { id: playerId, name: name });

    // Send avatar update using the network ID
    targetWorld.network.send('playerSessionAvatar', { avatar: avatarUrl });
}
// <-------------------------------------------

// Start the agent
runAgent()

async function uploadAndSetAvatar(agentPlayer) {
    let fileName = ''; // Define filename variable

    try {
        const filePath = path.resolve(__dirname, LOCAL_AVATAR_PATH); // Ensure absolute path
        console.log(`[Agent Appearance] Reading avatar file from: ${filePath}`);
        const fileBuffer = await fs.readFile(filePath); // Reads into a Buffer
        fileName = path.basename(filePath); // Assign to outer scope variable
        const mimeType = 'model/gltf-binary'; // Assuming VRM is glTF binary

        // Check necessary network properties are available
        if (!world.network || typeof world.network.upload !== 'function' || !world.assetsUrl) {
            console.error("[Agent Appearance] world.network.upload function or world.assetsUrl not available!");
            return false; // Indicate failure
        }

        console.log(`[Agent Appearance] Uploading ${fileName} (${(fileBuffer.length / 1024).toFixed(2)} KB)...`);

        // Hash the buffer directly
        console.log(`[Agent Appearance] Constructing expected HTTP(S) URL...`);
        const hash = await hashFileBuffer(fileBuffer); // Hash the buffer
        if (!hash) {
             console.error("[Agent Appearance] Failed to calculate file hash for URL construction.");
             return false;
        }
        const ext = fileName.split('.').pop().toLowerCase();

        // Construct URL relative to the assetsUrl
        const baseUrl = world.assetsUrl.replace(/\/$/, ''); // Remove trailing slash if present
        const constructedHttpUrl = `${baseUrl}/${hash}.${ext}`;

        console.log(`[Agent Appearance] Constructed HTTP(S) URL: ${constructedHttpUrl}`);

        // --- Upload the Buffer (adjust based on what world.network.upload expects) ---
        // Option 1: Pass an object with buffer and metadata (like in service.ts)
        const uploadData = {
            buffer: fileBuffer,
            name: fileName,
            type: mimeType,
            size: fileBuffer.length
        };
        await world.network.upload(uploadData); // TRY THIS FIRST
        // Option 2: Pass buffer directly (if Option 1 fails)
        // await world.network.upload(fileBuffer);
        // Option 3: Pass underlying ArrayBuffer (if Option 1/2 fail)
        // await world.network.upload(fileBuffer.buffer);
        console.log(`[Agent Appearance] Upload process initiated.`);
        // --------------------------------------------------------------------------

        // --- Setting the avatar using the constructed HTTP URL --- >
        // (This part remains the same as it uses the URL, not the blob/buffer)
        if (typeof agentPlayer.setSessionAvatar === 'function') {
            agentPlayer.setSessionAvatar(constructedHttpUrl); // Use the constructed HTTP URL
            console.log(`[Agent Appearance] Called setSessionAvatar with constructed URL: ${constructedHttpUrl}`);
            return true; // Indicate success
        } else if (world.network && typeof world.network.send === 'function') {
            // Fallback: Try sending a network message
             world.network.send('playerSessionAvatar', { avatar: constructedHttpUrl });
             console.log(`[Agent Appearance] Sent playerSessionAvatar network message with: ${constructedHttpUrl}`);
             return true;
        } else {
            console.error("[Agent Appearance] world.entities.player.setSessionAvatar method or network send not found!");
            return false; // Indicate failure
        }
        // <------------------------------------------------------

    } catch (error) {
        if (error.code === 'ENOENT') {
            console.error(`[Agent Appearance] Error: Avatar file not found at ${path.resolve(__dirname, LOCAL_AVATAR_PATH)}`);
        } else {
            console.error("[Agent Appearance] Error during avatar upload/set process:", error);
        }
        return false; // Indicate failure
    }
}

function startAppearancePolling() {
    if (appearanceIntervalId) clearInterval(appearanceIntervalId);
    console.log(`[Agent Appearance Polling] Initializing interval every 1000ms.`);

    appearanceIntervalId = setInterval(async () => { // Make the interval callback async
        const agentPlayer = world?.entities?.player;
        const networkReady = world?.network?.id != null;

        if (!appearanceSet && agentPlayer && networkReady) {
            console.log(`[Agent Appearance Polling] Player entity and network ready. Attempting to upload and set avatar...`);

            const success = await uploadAndSetAvatar(agentPlayer); // Call the new async function

            if (success) {
                appearanceSet = true; // Mark as set only on success
                clearInterval(appearanceIntervalId); // Stop polling
                appearanceIntervalId = null; // Clear the ID
                console.log(`[Agent Appearance Polling] Avatar successfully set. Polling stopped.`);
            } else {
                console.log(`[Agent Appearance Polling] Avatar setting failed, will retry...`);
                // Keep polling on failure
            }

        } else if (!appearanceSet) {
            // Still waiting
             // console.log(`[Agent Appearance Polling] Waiting for player (${!!agentPlayer}) and network (${networkReady})...`); // Optional verbose log
        }
    }, 3000); // Check every 3 seconds to give upload/set time and avoid spamming
}

// --- IMPLEMENTED Physics Geometry Setup ---
async function setupStaticPhysicsGeometry(world, gltf) {
     console.log("[Agent Physics] Starting setupStaticPhysicsGeometry...");
     if (!gltf || !gltf.scene) { /* ... error handling ... */ return; }
     
     const PHYSX = globalThis.PHYSX;
     if (!PHYSX) { /* ... error handling ... */ return; }
     
     const physics = world.physics?.physics;
     const scene = world.physics?.scene;
     // NOTE: geometryToPxMesh uses world.physics.cookingParams internally
     const material = world.physics?.material; 

     if (!physics || !scene || !material) { // Cooking is used internally by geometryToPxMesh
         console.error("[Agent Physics] Physics system components (physics, scene, material) not ready.");
         return;
     }
     console.log("[Agent Physics] PhysX components obtained.");
     
     // Reusable transform

     const physxTransform = new PHYSX.PxTransform(PHYSX.PxIdentityEnum.PxIdentity);

     let meshesProcessed = 0;
     let actorsAdded = 0;
     const traversalErrors = [];

     // Ensure world matrices are up-to-date before traversal
     gltf.scene.updateMatrixWorld(true); 

     gltf.scene.traverseVisible((node) => {
        if (node.isMesh && node.geometry) {
            console.log(`[Agent Physics] Processing mesh: ${node.name || '(unnamed)'}`);
            meshesProcessed++;
            let pmeshHandle = null;
            try {
                // --- Cook Mesh using Utility ---
                // Use convex=false for triangle mesh
                pmeshHandle = geometryToPxMesh(world, node.geometry, false); 
                
                if (!pmeshHandle || !pmeshHandle.value) {
                    throw new Error(`geometryToPxMesh returned null for mesh ${node.name || '(unnamed)'}`);
                }
                const cookedMesh = pmeshHandle.value; // The actual PxTriangleMesh
                 // console.log(`[Agent Physics] Cooked mesh for ${node.name || '(unnamed)'}.`);
                // -----------------------------

                // --- Create Geometry and Shape ---
                 const meshScale = new PHYSX.PxMeshScale(node.scale.toPxVec3(), {x:0, y:0, z:0, w:1}); // Apply mesh scale here!
                 // const meshScale = new PHYSX.PxMeshScale({x:1, y:1, z:1}, {x:0, y:0, z:0, w:1}); // Simpler if scale is baked? Test.
                const meshGeometry = new PHYSX.PxTriangleMeshGeometry(cookedMesh, meshScale, new PHYSX.PxMeshGeometryFlags(0));
                if (!meshGeometry.isValid()) {
                     throw new Error("Created PxTriangleMeshGeometry is invalid");
                }
                
                const shapeFlags = new PHYSX.PxShapeFlags(PHYSX.PxShapeFlagEnum.eSCENE_QUERY_SHAPE | PHYSX.PxShapeFlagEnum.eSIMULATION_SHAPE);
                const shape = physics.createShape(meshGeometry, material, true, shapeFlags);
                
                // --- Set Filter Data (Example: Environment layer 1, collides with Player layer 0) ---
                const filterData = new PHYSX.PxFilterData(1, 1 << 0, 0, 0); 
                shape.setSimulationFilterData(filterData);
                shape.setQueryFilterData(filterData);
                // ------------------------------------

                // --- Create Static Actor with World Transform ---
                node.matrixWorld.toPxTransform(physxTransform); // Get world transform of the mesh node
                const staticActor = physics.createRigidStatic(physxTransform); // Apply transform to actor
                // ---------------------------------------------

                staticActor.attachShape(shape);
                scene.addActor(staticActor);
                actorsAdded++;
                // console.log(`[Agent Physics] Added static actor for ${node.name || '(unnamed)'}.`);
                
            } catch(error) {
                 console.error(`[Agent Physics] Error processing mesh ${node.name || '(unnamed)'}:`, error);
                 traversalErrors.push(error);
            } finally {
                 // --- IMPORTANT: Release the handle ---
                 // This decrements the ref count in the cache
                 if (pmeshHandle) {
                      pmeshHandle.release(); 
                 }
                 // -----------------------------------
            }
        }
     });

     if (traversalErrors.length > 0) {
          console.warn(`[Agent Physics] Finished setupStaticPhysicsGeometry. Meshes processed: ${meshesProcessed}, Actors added: ${actorsAdded}, Errors: ${traversalErrors.length}.`);
     } else {
        console.log(`[Agent Physics] Finished setupStaticPhysicsGeometry. Meshes processed: ${meshesProcessed}, Actors added: ${actorsAdded}.`);
     }
}
