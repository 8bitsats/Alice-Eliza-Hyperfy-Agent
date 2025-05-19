import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Import Hyperfy's node client
import { createNodeClientWorld } from '../hyperfy/build/world-node-client.js';
import { AgentControls } from './AgentControls.js';
// Import our agent components
import { AgentLoader } from './AgentLoader.js';
// Import Alice Agent
import { AliceAgent } from './AliceAgent.mjs';

dotenv.config()

// Get the directory name
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Configuration
const WS_URL = process.env.WS_URL || 'ws://localhost:3000/ws'
const AGENT_NAME = process.env.AGENT_NAME || 'Alice in Wonderland'
const LOCAL_AVATAR_PATH = process.env.AVATAR_PATH || path.resolve(__dirname, './avatar.vrm')
const ALICE_BACKEND_URL = process.env.ALICE_BACKEND_URL || 'ws://localhost:8765'
const CHARACTER_PATH = process.env.CHARACTER_PATH || path.resolve(__dirname, './alice-config.json')
const DEBUG = process.env.DEBUG === 'true' || false

async function connectAgent() {
  console.log(`Connecting Alice agent to Hyperfy at ${WS_URL}...`)
  
  // Create the Hyperfy world with our custom agent components
  const world = createNodeClientWorld({
    controls: AgentControls,
    loader: AgentLoader
  })
  
  // Initialize the world with configuration
  await world.init({
    wsUrl: WS_URL,
    name: AGENT_NAME,
    // Use the avatar file if it exists
    avatar: LOCAL_AVATAR_PATH
  })
  
  console.log('Hyperfy world initialized')
  
  // Create Alice agent instance
  const alice = new AliceAgent(world, {
    aliceBackendUrl: ALICE_BACKEND_URL,
    characterPath: CHARACTER_PATH,
    debug: DEBUG,
    useMultiModel: true,
    useBlueSteelBrowser: true,
    usePhysics: true
  })
  
  // Store Alice instance on world for easy access
  world.alice = alice
  
  // Handle connection events
  world.once('ready', async () => {
    console.log('Agent connected and ready')
    
    // Start Alice agent
    try {
      await alice.start()
      console.log('Alice agent started successfully')
    } catch (error) {
      console.error('Failed to start Alice agent:', error)
    }
  })
  
  world.on('kick', (code) => {
    console.log(`Agent kicked: ${code}`)
    stopAlice(world)
  })
  
  world.on('disconnect', (reason) => {
    console.log(`Agent disconnected: ${reason}`)
    stopAlice(world)
    world.destroy()
  })
  
  // Handle process termination
  process.on('SIGINT', async () => {
    console.log('SIGINT received')
    await stopAlice(world)
    process.exit(0)
  })
  
  process.on('SIGTERM', async () => {
    console.log('SIGTERM received')
    await stopAlice(world)
    process.exit(0)
  })
  
  // Set up proximity detection for Alice
  setupProximityDetection(world, alice)
  
  return world
}

// Setup proximity detection for Alice to respond to nearby players
function setupProximityDetection(world, alice) {
  // Set up a interval to check for nearby players
  const checkProximity = setInterval(() => {
    if (!world.entities || !world.entities.player) return
    
    const alicePosition = world.entities.player.position
    
    // Get all avatars
    const avatars = Object.values(world.entities).filter(
      entity => entity.type === 'avatar' && entity.id !== world.entities.player.id
    )
    
    // Check distance to each avatar
    for (const avatar of avatars) {
      const position = avatar.position
      if (!position) continue
      
      const dx = position[0] - alicePosition[0]
      const dz = position[2] - alicePosition[2]
      const distance = Math.sqrt(dx * dx + dz * dz)
      
      // If player is within range, notify Alice
      if (distance < 5) {
        alice.onPlayerNearby(avatar, distance)
      }
    }
  }, 1000) // Check every second
  
  // Clean up on world destroy
  world.once('destroy', () => {
    clearInterval(checkProximity)
  })
}

async function stopAlice(world) {
  console.log('Stopping Alice...')
  
  // Stop Alice agent if it exists
  if (world.alice) {
    try {
      await world.alice.stop()
      console.log('Alice agent stopped successfully')
    } catch (error) {
      console.error('Error stopping Alice agent:', error)
    }
  }
  
  // Additional cleanup if needed
  if (world) {
    await world.destroy()
    console.log('World destroyed')
  }
}

// Export the connect function
export { connectAgent };

// Auto-run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  connectAgent().catch(err => {
    console.error('Error connecting agent:', err)
    process.exit(1)
  })
}
