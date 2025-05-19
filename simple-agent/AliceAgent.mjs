import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
// WebSocket for communication with the Eliza/Alice backend
import WebSocket from 'ws';

// AliceAgent class - Core implementation of Alice for Hyperfy
export class AliceAgent {
  constructor(world, config = {}) {
    // Store reference to Hyperfy world
    this.world = world;
    
    // Configuration for the agent
    this.config = {
      aliceBackendUrl: config.aliceBackendUrl || 'ws://localhost:8765',
      characterPath: config.characterPath || './alice_character.json',
      debug: config.debug || false,
      useMultiModel: config.useMultiModel || true,
      useBlueSteelBrowser: config.useBlueSteelBrowser || false,
      usePhysics: config.usePhysics || true,
      ...config
    };
    
    // Agent state
    this.state = {
      isConnected: false,
      isBackendConnected: false,
      isMoving: false,
      currentAnimation: 'idle',
      currentPosition: [0, 0, 0],
      currentRotation: [0, 0, 0, 1],
      activeModel: 'anthropic',
      isSpeaking: false,
      isThinking: false,
      browserActive: false,
      lastInteraction: Date.now(),
      chatHistory: []
    };
    
    // Backend WebSocket connection
    this.socket = null;
    
    // Movement/behavior timers and intervals
    this.movementInterval = null;
    this.idleAnimationInterval = null;
    this.lookAroundInterval = null;
    
    // Character definition loaded from JSON
    this.character = null;
    
    // Log initialization
    this._log('Alice agent initialized with config:', this.config);
  }
  
  // Load Alice's character definition from JSON
  async loadCharacter() {
    try {
      const __filename = fileURLToPath(import.meta.url);
      const __dirname = path.dirname(__filename);
      const characterPath = path.resolve(__dirname, this.config.characterPath);
      
      this._log(`Loading character from ${characterPath}`);
      
      const data = await fs.readFile(characterPath, 'utf-8');
      this.character = JSON.parse(data);
      
      this._log('Character loaded successfully');
      return this.character;
    } catch (error) {
      console.error('Error loading character definition:', error);
      // Use basic character definition as fallback
      this.character = {
        name: "Alice",
        bio: [
          "I am Alice, a curious explorer from Wonderland now navigating the digital metaverse with wide-eyed wonder."
        ],
        style: {
          all: ["I speak with a sense of wonder and curiosity about everything I encounter."]
        }
      };
      return this.character;
    }
  }
  
  // Connect to the Alice backend (Python)
  async connectToBackend() {
    this._log(`Connecting to Alice backend at ${this.config.aliceBackendUrl}`);
    
    return new Promise((resolve, reject) => {
      // Create WebSocket connection
      this.socket = new WebSocket(this.config.aliceBackendUrl);
      
      // Set up event handlers
      this.socket.onopen = () => {
        this._log('Connected to Alice backend');
        this.state.isBackendConnected = true;
        resolve(true);
      };
      
      this.socket.onclose = () => {
        this._log('Disconnected from Alice backend');
        this.state.isBackendConnected = false;
        this.scheduleReconnect();
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.state.isBackendConnected = false;
        reject(error);
      };
      
      this.socket.onmessage = this.handleBackendMessage.bind(this);
      
      // Set timeout for connection
      const timeout = setTimeout(() => {
        if (!this.state.isBackendConnected) {
          this._log('Connection to backend timed out');
          reject(new Error('Connection timeout'));
        }
      }, 10000);
      
      // Clear timeout on successful connection
      this.socket.onopen = () => {
        clearTimeout(timeout);
        this._log('Connected to Alice backend');
        this.state.isBackendConnected = true;
        this.sendStateToBackend();
        resolve(true);
      };
    });
  }
  
  // Attempt to reconnect to backend if disconnected
  scheduleReconnect() {
    this._log('Scheduling reconnection to backend...');
    setTimeout(async () => {
      if (!this.state.isBackendConnected) {
        try {
          await this.connectToBackend();
        } catch (error) {
          console.error('Reconnection failed:', error);
          this.scheduleReconnect();
        }
      }
    }, 5000);
  }
  
  // Handle messages from the Alice backend
  handleBackendMessage(event) {
    try {
      const message = JSON.parse(event.data);
      this._log('Received message from backend:', message);
      
      switch (message.type) {
        case 'STATE_UPDATE':
          this.updateStateFromBackend(message.state);
          break;
          
        case 'AUDIO':
          this.playAudio(message.data);
          break;
          
        case 'BROWSER_CONTENT':
          // Currently we don't have a way to show browser content in Hyperfy directly
          // This would be handled by the UI in the real application
          this._log('Received browser content');
          break;
          
        case 'PHYSICS_UPDATE':
          this.updatePhysicsObjects(message.objects);
          break;
          
        default:
          this._log(`Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error('Error handling backend message:', error);
    }
  }
  
  // Update agent state based on backend state
  updateStateFromBackend(backendState) {
    // Update position if provided and different
    if (backendState.position && 
        JSON.stringify(backendState.position) !== JSON.stringify(this.state.currentPosition)) {
      this.state.currentPosition = backendState.position;
      this.moveToPosition(backendState.position);
    }
    
    // Update rotation if provided and different
    if (backendState.rotation && 
        JSON.stringify(backendState.rotation) !== JSON.stringify(this.state.currentRotation)) {
      this.state.currentRotation = backendState.rotation;
      this.rotateTo(backendState.rotation);
    }
    
    // Update speaking state
    if (backendState.speaking !== undefined) {
      this.state.isSpeaking = backendState.speaking;
      if (backendState.speaking) {
        this.setAnimation('talking');
      } else if (!this.state.isMoving && !this.state.isThinking) {
        this.setAnimation('idle');
      }
    }
    
    // Update thinking state
    if (backendState.thinking !== undefined) {
      this.state.isThinking = backendState.thinking;
      if (backendState.thinking) {
        this.setAnimation('thinking');
      } else if (!this.state.isMoving && !this.state.isSpeaking) {
        this.setAnimation('idle');
      }
    }
    
    // Update browser state
    if (backendState.browser_active !== undefined) {
      this.state.browserActive = backendState.browser_active;
      if (backendState.browser_active) {
        this.setAnimation('browsing');
      } else if (!this.state.isMoving && !this.state.isSpeaking && !this.state.isThinking) {
        this.setAnimation('idle');
      }
    }
    
    // Update active model
    if (backendState.current_model) {
      this.state.activeModel = backendState.current_model;
    }
    
    // Update animations if provided
    if (backendState.animations && backendState.animations.length > 0) {
      this.setAnimation(backendState.animations[0]);
    }
  }
  
  // Send current state to backend
  sendStateToBackend() {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return;
    }
    
    const state = {
      position: this.state.currentPosition,
      rotation: this.state.currentRotation,
      animation: this.state.currentAnimation,
      interacting: this.isInteracting()
    };
    
    this.socket.send(JSON.stringify({
      type: 'STATE_UPDATE',
      state
    }));
  }
  
  // Send voice input to backend
  sendVoiceInput(text) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this._log('Cannot send voice input: not connected to backend');
      return;
    }
    
    this._log(`Sending voice input: ${text}`);
    
    this.socket.send(JSON.stringify({
      type: 'VOICE_INPUT',
      text
    }));
    
    // Add to chat history
    this.state.chatHistory.push({
      sender: 'user',
      text,
      timestamp: Date.now()
    });
  }
  
  // Send action to backend
  sendAction(action, params = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this._log(`Cannot send action ${action}: not connected to backend`);
      return;
    }
    
    this._log(`Sending action: ${action}`, params);
    
    this.socket.send(JSON.stringify({
      type: 'ACTION',
      action,
      params
    }));
  }
  
  // Check if agent is currently interacting with a user
  isInteracting() {
    return (Date.now() - this.state.lastInteraction) < 60000; // 1 minute timeout
  }
  
  // Update the interaction timestamp
  updateInteraction() {
    this.state.lastInteraction = Date.now();
    this.sendStateToBackend();
  }
  
  // Handle incoming chat messages from Hyperfy
  handleIncomingChat(message) {
    this._log(`Received chat message: ${message.body} from ${message.from}`);
    
    // Ignore messages from self
    if (message.fromId === this.world.entities?.player?.id) {
      return;
    }
    
    // Process message with backend
    this.sendVoiceInput(message.body);
    this.updateInteraction();
  }
  
  // Play audio from the backend
  playAudio(audioBase64) {
    // In a real implementation, this would play the audio through Hyperfy's audio system
    this._log('Audio playback requested');
    
    // Example implementation if Hyperfy has an API for this:
    // this.world.playAudio({
    //   data: audioBase64,
    //   position: this.state.currentPosition
    // });
  }
  
  // Update physics objects from backend
  updatePhysicsObjects(objects) {
    // This would update the physics objects in Hyperfy based on the backend simulation
    this._log(`Updating ${Object.keys(objects).length} physics objects`);
    
    // Example implementation:
    // Object.entries(objects).forEach(([id, data]) => {
    //   const object = this.world.getEntityById(id);
    //   if (object) {
    //     object.setPosition(data.position);
    //     object.setRotation(data.rotation);
    //   }
    // });
  }
  
  // Move agent to specified position
  moveToPosition(position) {
    this._log(`Moving to position: ${position}`);
    this.state.isMoving = true;
    this.setAnimation('walking');
    
    // In a real implementation, this would use Hyperfy's movement API
    // Example:
    // this.world.player.setPosition(position);
    
    // For now, just update our state directly
    this.state.currentPosition = position;
    
    // Simulate movement completion
    setTimeout(() => {
      this.state.isMoving = false;
      if (!this.state.isSpeaking && !this.state.isThinking && !this.state.browserActive) {
        this.setAnimation('idle');
      }
    }, 1000);
  }
  
  // Rotate agent to specified orientation
  rotateTo(rotation) {
    this._log(`Rotating to: ${rotation}`);
    
    // In a real implementation, this would use Hyperfy's rotation API
    // Example:
    // this.world.player.setRotation(rotation);
    
    // For now, just update our state directly
    this.state.currentRotation = rotation;
  }
  
  // Set current animation
  setAnimation(animation) {
    if (this.state.currentAnimation === animation) {
      return;
    }
    
    this._log(`Setting animation: ${animation}`);
    this.state.currentAnimation = animation;
    
    // In a real implementation, this would use Hyperfy's animation system
    // Example:
    // this.world.player.setAnimation(animation);
  }
  
  // Respond to nearby player detection
  onPlayerNearby(player, distance) {
    this._log(`Player ${player.name} nearby at distance ${distance}`);
    
    // If we're not already interacting with someone
    if (!this.isInteracting()) {
      // Look at the player
      this.lookAt(player.position);
      
      // Wave and greet
      this.setAnimation('wave');
      
      // Send greeting to backend for voice response
      const greeting = this.getRandomGreeting();
      this.sendVoiceInput(greeting);
      
      // Update interaction state
      this.updateInteraction();
      
      // Reset to idle after greeting
      setTimeout(() => {
        if (!this.state.isSpeaking && !this.state.isThinking) {
          this.setAnimation('idle');
        }
      }, 3000);
    }
  }
  
  // Get random greeting from character definition
  getRandomGreeting() {
    const defaultGreetings = [
      "Hello there! Welcome to Wonderland!",
      "Oh! A visitor! How curious and wonderful!",
      "Greetings! Have you fallen down the rabbit hole too?"
    ];
    
    if (this.character && this.character.greetings && this.character.greetings.length > 0) {
      const index = Math.floor(Math.random() * this.character.greetings.length);
      return this.character.greetings[index];
    }
    
    const index = Math.floor(Math.random() * defaultGreetings.length);
    return defaultGreetings[index];
  }
  
  // Look at a specific position
  lookAt(position) {
    this._log(`Looking at position: ${position}`);
    
    // Calculate direction vector
    const direction = [
      position[0] - this.state.currentPosition[0],
      0, // Ignore Y difference
      position[2] - this.state.currentPosition[2]
    ];
    
    // Normalize and convert to rotation
    const length = Math.sqrt(direction[0]**2 + direction[2]**2);
    if (length > 0) {
      const normalizedDir = [direction[0]/length, 0, direction[2]/length];
      const angle = Math.atan2(normalizedDir[0], normalizedDir[2]);
      
      // Convert to quaternion (simplified)
      const rotation = [0, Math.sin(angle/2), 0, Math.cos(angle/2)];
      this.rotateTo(rotation);
      
      // Also send to backend
      this.sendAction('rotate', {
        rotation
      });
    }
  }
  
  // Start idle behaviors
  startIdleBehaviors() {
    this._log('Starting idle behaviors');
    
    // Random idle animations
    this.idleAnimationInterval = setInterval(() => {
      if (!this.isInteracting() && !this.state.isMoving && !this.state.isSpeaking && !this.state.isThinking) {
        const animations = ['idle', 'curious', 'thinking'];
        const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
        this.setAnimation(randomAnimation);
        
        // Reset to idle after a short time
        setTimeout(() => {
          if (!this.isInteracting() && !this.state.isMoving && !this.state.isSpeaking && !this.state.isThinking) {
            this.setAnimation('idle');
          }
        }, 3000);
      }
    }, 30000); // Every 30 seconds
    
    // Look around occasionally
    this.lookAroundInterval = setInterval(() => {
      if (!this.isInteracting() && !this.state.isMoving) {
        // Generate random angle
        const angle = Math.random() * Math.PI * 2;
        const rotation = [0, Math.sin(angle/2), 0, Math.cos(angle/2)];
        this.rotateTo(rotation);
      }
    }, 15000); // Every 15 seconds
  }
  
  // Stop idle behaviors
  stopIdleBehaviors() {
    this._log('Stopping idle behaviors');
    
    if (this.idleAnimationInterval) {
      clearInterval(this.idleAnimationInterval);
      this.idleAnimationInterval = null;
    }
    
    if (this.lookAroundInterval) {
      clearInterval(this.lookAroundInterval);
      this.lookAroundInterval = null;
    }
  }
  
  // Start agent
  async start() {
    this._log('Starting Alice agent');
    
    // Load character definition
    await this.loadCharacter();
    
    // Connect to backend
    try {
      await this.connectToBackend();
    } catch (error) {
      console.error('Failed to connect to backend:', error);
      // Continue anyway, will try to reconnect later
    }
    
    // Set up chat listener
    if (this.world.chat) {
      this.world.chat.subscribe(this.handleIncomingChat.bind(this));
    }
    
    // Start idle behaviors
    this.startIdleBehaviors();
    
    // Set initial animation
    this.setAnimation('idle');
    
    // Set connection status
    this.state.isConnected = true;
    
    return true;
  }
  
  // Stop agent
  async stop() {
    this._log('Stopping Alice agent');
    
    // Stop behaviors
    this.stopIdleBehaviors();
    
    // Close backend connection
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    // Set connection status
    this.state.isConnected = false;
    
    return true;
  }
  
  // Internal logging helper
  _log(...args) {
    if (this.config.debug) {
      console.log('[AliceAgent]', ...args);
    }
  }
}
