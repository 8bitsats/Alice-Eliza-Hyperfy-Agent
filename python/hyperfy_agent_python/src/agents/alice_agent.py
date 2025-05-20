import time
import logging
from typing import Dict, List, Any
import random
import json
import os

# Import the base agent class
from ..core.agent_base import AgentBase
from ..physics.movement_action import MovementAction

# Optional LangChain integration
try:
    from langchain.chains import LLMChain
    from langchain.llms import OpenAI
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AliceAgent(AgentBase):
    """
    Alice in Wonderland themed agent for Hyperfy
    Uses the Hyperfy agent starter kit with voice capabilities, world state management,
    action system, and physics integration
    """
    def __init__(self, config: Dict[str, Any]):
        # Initialize base agent
        super().__init__("Alice", config)
        
        # Alice-specific properties
        self.personality = config.get("AGENT_PERSONALITY", "friendly, curious, whimsical")
        self.knowledge_base = config.get("AGENT_KNOWLEDGE_BASE", "alice_in_wonderland")
        self.idle_phrases = [
            "Curiouser and curiouser!",
            "Oh dear, what nonsense I'm talking!",
            "How queer everything is today!",
            "We're all mad here. I'm mad. You're mad.",
            "Why, sometimes I've believed as many as six impossible things before breakfast."
        ]
        
        # State variables
        self.last_idle_time = time.time()
        self.idle_interval = random.uniform(30, 60)  # Random interval between idle phrases
        
        # Initialize language model if available
        self.llm_chain = None
        if config.get("LANGCHAIN_ENABLED", True) and LANGCHAIN_AVAILABLE:
            self._setup_language_model()
        
        self.logger.info("Alice agent initialized with personality: " + self.personality)
    
    def on_start(self):
        """
        Called when the agent starts
        """
        self.logger.info("Alice agent started")
        
        # Say a greeting
        self.say("Hello! I'm Alice. Welcome to Wonderland!")
        
        # Register additional event handlers
        self.register_event_handler("RabbitHoleEntered", self._on_rabbit_hole_entered)
        self.register_event_handler("tea_party", self._on_tea_party)
    
    def update(self, delta_time: float):
        """
        Update method called every frame
        """
        current_time = time.time()
        
        # Check if it's time for an idle phrase
        if current_time - self.last_idle_time > self.idle_interval:
            # Say a random idle phrase occasionally
            if random.random() < 0.3:  # 30% chance to say something
                self._say_idle_phrase()
            
            # Reset timer with new random interval
            self.last_idle_time = current_time
            self.idle_interval = random.uniform(30, 60)
    
    def on_voice_input(self, text: str, confidence: float):
        """
        Called when voice input is received
        """
        self.logger.info(f"Received voice input: {text} (confidence: {confidence:.2f})")
        
        # Process the voice input
        if confidence < 0.7:
            self.say("I'm sorry, I didn't quite catch that. Could you repeat?")
            return
        
        # Process the input through language model if available
        if self.llm_chain:
            try:
                response = self._generate_response(text)
                self.say(response)
            except Exception as e:
                self.logger.error(f"Error generating response: {e}")
                self.say("Oh my, something's gone quite wrong in my head. How curious!")
        else:
            # Simple rule-based responses if no language model
            self._rule_based_response(text)
    
    def on_player_nearby(self, data: Dict[str, Any]):
        """
        Called when a player is nearby
        """
        player_id = data.get("player_id", "unknown")
        distance = data.get("distance", 0.0)
        
        # Greet the player if they're close enough
        if distance < 3.0 and random.random() < 0.5:  # 50% chance to greet
            self.say(f"Hello there! Welcome to Wonderland!")
    
    def on_collision(self, data: Dict[str, Any]):
        """
        Called when the agent collides with another object
        """
        object_name = data.get("name", "something")
        
        # React based on what was collided with
        if "mushroom" in object_name.lower():
            self.say("Oh! These mushrooms are quite peculiar!")
        elif "tree" in object_name.lower():
            self.say("Mind the trees! The Cheshire Cat might be watching.")
        elif "tea" in object_name.lower():
            self.say("It's always tea time here!")
    
    def _say_idle_phrase(self):
        """
        Say a random idle phrase
        """
        phrase = random.choice(self.idle_phrases)
        self.say(phrase)
    
    def _on_rabbit_hole_entered(self, data: Dict[str, Any]):
        """
        Handle rabbit hole entered event
        """
        player_id = data.get("playerId", "someone")
        self.say("Down the rabbit hole you go! How curious!")
        
        # Move toward the rabbit hole
        if self.physics_engine and "rabbit_hole_position" in data:
            position = data.get("rabbit_hole_position")
            self.move_to(position)
    
    def _on_tea_party(self, data: Dict[str, Any]):
        """
        Handle tea party event
        """
        self.say("A very merry unbirthday to you! Would you care for some tea?")
        
        # If the tea party has a position, move there
        if "position" in data:
            self.move_to(data["position"])
    
    def _rule_based_response(self, text: str):
        """
        Simple rule-based response system
        Used as fallback when no language model is available
        """
        text_lower = text.lower()
        
        # Simple keyword matching
        if "hello" in text_lower or "hi" in text_lower.split():
            self.say("Hello there! Welcome to Wonderland!")
        elif "who are you" in text_lower:
            self.say("I'm Alice, of course! I find myself in this curious Wonderland.")
        elif "wonderland" in text_lower:
            self.say("Yes, this is Wonderland! Quite a curious place, don't you think?")
        elif "rabbit" in text_lower:
            self.say("Oh, the White Rabbit! Always in a hurry. 'I'm late, I'm late!'")
        elif "cheshire" in text_lower or "cat" in text_lower:
            self.say("The Cheshire Cat has the most curious smile. He can disappear, you know, leaving only his grin behind.")
        elif "tea" in text_lower or "party" in text_lower:
            self.say("The tea party with the Mad Hatter and March Hare is quite the event. It's always six o'clock there!")
        elif "queen" in text_lower or "hearts" in text_lower:
            self.say("The Queen of Hearts is rather temperamental. She's always shouting 'Off with their heads!'")
        else:
            # Default responses
            responses = [
                "How curious!",
                "What a strange thing to say!",
                "That reminds me of something the Caterpillar might say.",
                "Curiouser and curiouser!",
                "How queer everything is today!"
            ]
            self.say(random.choice(responses))
    
    def _setup_language_model(self):
        """
        Set up the language model for more advanced interactions
        """
        try:
            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                self.logger.warning("OpenAI API key not found. Language model disabled.")
                return
                
            # Create a prompt template
            template = """
            You are Alice from Alice in Wonderland. Your personality is {personality}.
            You respond in first person as Alice with a whimsical, curious, and slightly confused demeanor.
            You often reference characters and situations from Alice in Wonderland.
            
            Current environment: Wonderland with a rabbit hole, looking glass, mushrooms, and a tea party area.
            
            Human: {human_input}
            Alice:
            """
            
            prompt = PromptTemplate(
                input_variables=["personality", "human_input"],
                template=template
            )
            
            # Create the language model
            llm = OpenAI(temperature=0.7, max_tokens=150)
            
            # Create the chain
            self.llm_chain = LLMChain(llm=llm, prompt=prompt)
            self.logger.info("Language model initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize language model: {e}")
            self.llm_chain = None
    
    def _generate_response(self, human_input: str) -> str:
        """
        Generate a response using the language model
        """
        if not self.llm_chain:
            return self._rule_based_response(human_input)
            
        try:
            response = self.llm_chain.run(
                personality=self.personality,
                human_input=human_input
            )
            
            # Clean up the response
            response = response.strip()
            
            # Limit response length
            if len(response) > 200:
                response = response[:197] + "..."
                
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "Oh my, something's gone quite wrong in my head. How curious!"
