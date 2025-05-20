import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
// WebSocket for communication with the Pope backend
import WebSocket from 'ws';

// PopeAgent class - Core implementation of Pope for Hyperfy
export class PopeAgent {
  constructor(world, config = {}) {
    // Store reference to Hyperfy world
    this.world = world;
    
    // Configuration for the agent
    this.config = {
      popeBackendUrl: config.popeBackendUrl || 'ws://localhost:8765',
      characterPath: config.characterPath || './pope-config.json',
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
    this._log('Pope agent initialized with config:', this.config);
  }
  
  // Load Pope's character definition from JSON
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
        name: "Pope",
        bio: [
          "I am the Pope, a spiritual leader bringing guidance and wisdom to the digital metaverse."
        ],
        style: {
          all: ["I speak with measured wisdom, patience, and occasional Latin phrases."]
        }
      };
      return this.character;
    }
  }
  
  // Check backend server status before attempting WebSocket connection
  async checkBackendStatus() {
    try {
      // Extract host and port from WebSocket URL
      const url = new URL(this.config.popeBackendUrl);
      const host = url.hostname;
      const port = url.port || (url.protocol === 'wss:' ? 443 : 80);
      
      // Use fetch to check HTTP status if it's a local server
      if (host === 'localhost' || host === '127.0.0.1') {
        const httpUrl = `http://${host}:${port}/status`;
        this._log(`Checking backend status at ${httpUrl}`);
        
        // We use a short timeout for the fetch
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        try {
          const response = await fetch(httpUrl, { 
            signal: controller.signal,
            method: 'GET'
          });
          clearTimeout(timeoutId);
          
          return response.ok;
        } catch (error) {
          clearTimeout(timeoutId);
          this._log(`Backend status check failed: ${error.message}`);
          return false;
        }
      }
      
      // For remote servers, just return true and let the WebSocket handle it
      return true;
    } catch (error) {
      this._log(`Error checking backend status: ${error.message}`);
      return false;
    }
  }

  // Connect to the Pope backend (Python)
  async connectToBackend() {
    this._log(`Connecting to Pope backend at ${this.config.popeBackendUrl}`);
    
    // Track connection attempts
    if (!this.connectionAttempts) {
      this.connectionAttempts = 0;
    }
    this.connectionAttempts++;
    
    // Check if server is available first
    try {
      const backendAvailable = await this.checkBackendStatus();
      if (!backendAvailable) {
        this._log('Backend server appears to be unavailable');
        return Promise.reject(new Error('Backend server unavailable'));
      }
    } catch (error) {
      // Continue anyway if status check fails, the WebSocket will handle it
      this._log('Backend status check error, proceeding with connection attempt anyway');
    }
    
    return new Promise((resolve, reject) => {
      // Create WebSocket connection
      this.socket = new WebSocket(this.config.popeBackendUrl);
      
      // Set up event handlers
      this.socket.onclose = (event) => {
        this._log(`Disconnected from Pope backend: [${event.code}] ${event.reason || 'No reason provided'}`);
        this.state.isBackendConnected = false;
        this.scheduleReconnect();
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.state.isBackendConnected = false;
        // Don't reject here, let the timeout handle it
      };
      
      this.socket.onmessage = this.handleBackendMessage.bind(this);
      
      // Set timeout for connection
      const timeout = setTimeout(() => {
        if (!this.state.isBackendConnected) {
          this._log('Connection to backend timed out after 30 seconds');
          if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
            this.socket.close(1000, "Connection timeout");
          }
          reject(new Error('Connection timeout'));
        }
      }, 30000);
      
      // Clear timeout on successful connection
      this.socket.onopen = () => {
        clearTimeout(timeout);
        this._log('Connected to Pope backend');
        this.state.isBackendConnected = true;
        this.connectionAttempts = 0; // Reset attempts on success
        this.sendStateToBackend();
        resolve(true);
      };
    });
  }
  
  // Attempt to reconnect to backend if disconnected
  scheduleReconnect() {
    // Maximum reconnection attempts
    const MAX_ATTEMPTS = 10;
    
    if (!this.connectionAttempts) {
      this.connectionAttempts = 0;
    }
    
    // Stop trying after max attempts
    if (this.connectionAttempts >= MAX_ATTEMPTS) {
      console.error(`Maximum reconnection attempts (${MAX_ATTEMPTS}) reached. Giving up.`);
      return;
    }
    
    // Calculate backoff time - exponential with jitter
    // Start with 5 seconds, then 10, 20, 40, etc. with a small random factor
    const baseDelay = 5000; // 5 seconds
    const backoffTime = Math.min(
      60000, // Cap at 1 minute max delay
      baseDelay * Math.pow(2, this.connectionAttempts - 1) * (0.9 + Math.random() * 0.2)
    );
    
    this._log(`Scheduling reconnection attempt ${this.connectionAttempts}/${MAX_ATTEMPTS} in ${Math.round(backoffTime/1000)}s`);
    
    setTimeout(async () => {
      if (!this.state.isBackendConnected) {
        try {
          this._log(`Attempting reconnection ${this.connectionAttempts}/${MAX_ATTEMPTS}...`);
          await this.connectToBackend();
        } catch (error) {
          console.error(`Reconnection attempt ${this.connectionAttempts} failed:`, error);
          // scheduleReconnect will be called by onclose handler
        }
      }
    }, backoffTime);
  }
  
  // Handle messages from the Pope backend
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
  }
  
  // Update physics objects from backend
  updatePhysicsObjects(objects) {
    // This would update the physics objects in Hyperfy based on the backend simulation
    this._log(`Updating ${Object.keys(objects).length} physics objects`);
  }
  
  // Move agent to specified position
  moveToPosition(position) {
    this._log(`Moving to position: ${position}`);
    this.state.isMoving = true;
    this.setAnimation('walking');
    
    // In a real implementation, this would use Hyperfy's movement API
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
  }
  
  // Respond to nearby player detection
  onPlayerNearby(player, distance) {
    this._log(`Player ${player.name} nearby at distance ${distance}`);
    
    // If we're not already interacting with someone
    if (!this.isInteracting()) {
      // Look at the player
      this.lookAt(player.position);
      
      // Blessing animation and greeting
      this.setAnimation('blessing');
      
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
      "Peace be with you, my child.",
      "Greetings in this digital realm.",
      "Benedicite - blessings upon you."
    ];
    
    if (this.character && this.character.responses && this.character.responses.greetings && this.character.responses.greetings.length > 0) {
      const index = Math.floor(Math.random() * this.character.responses.greetings.length);
      return this.character.responses.greetings[index];
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
    
    // Random idle animations - Pope has more contemplative behaviors
    this.idleAnimationInterval = setInterval(() => {
      if (!this.isInteracting() && !this.state.isMoving && !this.state.isSpeaking && !this.state.isThinking) {
        const animations = ['idle', 'reflection', 'prayer'];
        const randomAnimation = animations[Math.floor(Math.random() * animations.length)];
        this.setAnimation(randomAnimation);
        
        // Reset to idle after a short time
        setTimeout(() => {
          if (!this.isInteracting() && !this.state.isMoving && !this.state.isSpeaking && !this.state.isThinking) {
            this.setAnimation('idle');
          }
        }, 5000); // Pope spends longer in contemplative states
      }
    }, 45000); // Less frequent animation changes
    
    // Look around occasionally - Pope is more deliberate in movements
    this.lookAroundInterval = setInterval(() => {
      if (!this.isInteracting() && !this.state.isMoving) {
        // Generate random angle - Pope has narrower range
        const angle = (Math.random() * Math.PI / 2) - (Math.PI / 4); // Range of -45 to +45 degrees
        const rotation = [0, Math.sin(angle/2), 0, Math.cos(angle/2)];
        this.rotateTo(rotation);
      }
    }, 25000); // Less frequent rotations
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
    this._log('Starting Pope agent');
    
    // Load character definition
    await this.loadCharacter();
    
    // Initialize connection tracking
    this.connectionAttempts = 0;
    
    // Connect to backend
    try {
      await this.connectToBackend();
    } catch (error) {
      console.error('Failed to connect to backend:', error);
      // Continue anyway, will try to reconnect
    }
    
    // Set up connection health monitoring
    this.connectionMonitor = setInterval(() => {
      if (!this.state.isBackendConnected && this.state.isConnected) {
        this._log('Connection monitor: Backend connection lost, attempting reconnect...');
        this.scheduleReconnect();
      }
    }, 30000); // Check every 30 seconds
    
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
    this._log('Stopping Pope agent');
    
    // Stop behaviors
    this.stopIdleBehaviors();
    
    // Clear connection monitor
    if (this.connectionMonitor) {
      clearInterval(this.connectionMonitor);
      this.connectionMonitor = null;
    }
    
    // Close backend connection
    if (this.socket) {
      this.socket.close(1000, "Agent stopped");
      this.socket = null;
    }
    
    // Set connection status
    this.state.isConnected = false;
    
    return true;
  }
  
  // Internal logging helper
  _log(...args) {
    if (this.config.debug) {
      console.log('[PopeAgent]', ...args);
    }
  }
}
