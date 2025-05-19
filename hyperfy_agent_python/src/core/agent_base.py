import time
import threading
import logging
from typing import Dict, List, Any, Callable, Optional

from ..voice.voice_manager import VoiceManager
from ..physics.physics_engine import PhysicsEngine
from .world_state import WorldState
from .action_system import ActionSystem, Action

class AgentBase:
    """
    Base class for all Hyperfy agents
    Provides core functionality for agent systems including:
    - Voice capabilities
    - World state management
    - Action system
    - Physics integration
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialize core systems
        self.world_state = WorldState()
        self.action_system = ActionSystem(config.get("ACTION_COOLDOWN", 1.0))
        self.voice_manager = VoiceManager(config) if config.get("VOICE_RECOGNITION_ENABLED", True) else None
        self.physics_engine = PhysicsEngine(config) if config.get("PHYSICS_ENABLED", True) else None
        
        # State variables
        self.is_running = False
        self.last_update_time = 0
        self.update_thread = None
        self.event_handlers = {}
        
        # Agent properties
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.velocity = [0, 0, 0]
        
        self.logger.info(f"Agent {name} initialized with config: {config}")
    
    def start(self):
        """
        Start the agent's update loop and all subsystems
        """
        if self.is_running:
            self.logger.warning("Agent is already running")
            return
            
        self.logger.info(f"Starting agent {self.name}")
        self.is_running = True
        self.last_update_time = time.time()
        
        # Start subsystems
        if self.voice_manager:
            self.voice_manager.start(self._on_voice_input)
            
        if self.physics_engine:
            self.physics_engine.start()
            self._register_with_physics_engine()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Register default events
        self._register_default_event_handlers()
        
        self.on_start()
    
    def stop(self):
        """
        Stop the agent and all subsystems
        """
        if not self.is_running:
            return
            
        self.logger.info(f"Stopping agent {self.name}")
        self.is_running = False
        
        # Stop subsystems
        if self.voice_manager:
            self.voice_manager.stop()
            
        if self.physics_engine:
            self.physics_engine.stop()
        
        # Wait for update thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
        
        self.on_stop()
    
    def _update_loop(self):
        """
        Main update loop running on its own thread
        """
        while self.is_running:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Update all subsystems
            self.update(delta_time)
            
            # Process pending actions
            self.action_system.update(delta_time)
            
            # Sleep to maintain reasonable CPU usage
            time.sleep(0.016)  # ~60 FPS
    
    def update(self, delta_time: float):
        """
        Update method called every frame
        Can be overridden by subclasses
        """
        pass
    
    def on_start(self):
        """
        Called when the agent starts
        Can be overridden by subclasses
        """
        pass
    
    def on_stop(self):
        """
        Called when the agent stops
        Can be overridden by subclasses
        """
        pass
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """
        Register a function to handle a specific event
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Registered handler for event: {event_name}")
    
    def emit_event(self, event_name: str, data: Dict[str, Any] = None):
        """
        Emit an event to all registered handlers
        """
        if not data:
            data = {}
            
        data["source"] = self.name
        data["timestamp"] = time.time()
        
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_name}: {e}")
        
        self.logger.debug(f"Emitted event: {event_name} with data: {data}")
    
    def queue_action(self, action: Action):
        """
        Add an action to the action queue
        """
        return self.action_system.queue_action(action)
    
    def say(self, text: str, voice_id: str = None):
        """
        Make the agent speak using text-to-speech
        """
        if not self.voice_manager:
            self.logger.warning(f"Voice not enabled, can't say: {text}")
            return False
            
        # Use default voice if none specified
        if not voice_id:
            voice_id = self.config.get("AGENT_VOICE_ID", "default")
            
        return self.voice_manager.speak(text, voice_id)
    
    def move_to(self, position: List[float], speed: float = 1.0):
        """
        Move the agent to a specific position
        """
        from ..physics.movement_action import MovementAction
        action = MovementAction(self, position, speed)
        return self.queue_action(action)
    
    def _on_voice_input(self, text: str, confidence: float):
        """
        Handle voice input from the voice recognition system
        """
        self.logger.info(f"Voice input: '{text}' (confidence: {confidence:.2f})")
        
        # Emit voice input event
        self.emit_event("voice_input", {"text": text, "confidence": confidence})
        
        # Call the overridable method
        self.on_voice_input(text, confidence)
    
    def on_voice_input(self, text: str, confidence: float):
        """
        Called when voice input is received
        Can be overridden by subclasses
        """
        pass
    
    def _register_with_physics_engine(self):
        """
        Register the agent with the physics engine
        """
        if self.physics_engine:
            self.physics_engine.register_agent(self)
    
    def _register_default_event_handlers(self):
        """
        Register default event handlers
        """
        self.register_event_handler("collision", self._on_collision)
        self.register_event_handler("player_nearby", self._on_player_nearby)
    
    def _on_collision(self, data: Dict[str, Any]):
        """
        Default collision handler
        """
        self.logger.debug(f"Collision detected: {data}")
        self.on_collision(data)
    
    def on_collision(self, data: Dict[str, Any]):
        """
        Called when the agent collides with another object
        Can be overridden by subclasses
        """
        pass
    
    def _on_player_nearby(self, data: Dict[str, Any]):
        """
        Default handler for when a player is nearby
        """
        self.logger.debug(f"Player nearby: {data}")
        self.on_player_nearby(data)
    
    def on_player_nearby(self, data: Dict[str, Any]):
        """
        Called when a player is nearby
        Can be overridden by subclasses
        """
        pass
