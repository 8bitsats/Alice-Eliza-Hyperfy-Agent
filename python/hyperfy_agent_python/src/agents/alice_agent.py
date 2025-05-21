import time
import logging
from typing import Dict, List, Any
import random
import json
import os

# Import the base agent class
from ..core.agent_base import AgentBase
from ..physics.movement_action import MovementAction
from ..core.custom_actions import WalkRandomlyAction, StopMovingAction, UseItemAction, UnuseItemAction

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
        self.last_proactive_check_time = time.time()
        self.proactive_check_interval = random.uniform(15, 20)
        self.greeted_players_today: Dict[str, float] = {} # player_id: timestamp
        self.greeting_cooldown = 300 # 5 minutes in seconds
        
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

        # Proactive greeting check
        if current_time - self.last_proactive_check_time > self.proactive_check_interval:
            self._proactive_greeting_check(current_time)
            self.last_proactive_check_time = current_time
            self.proactive_check_interval = random.uniform(15, 25) # Reset interval
    
    def on_voice_input(self, text: str, confidence: float):
        """
        Called when voice input is received
        """
        self.logger.info(f"Received voice input: {text} (confidence: {confidence:.2f})")

        if confidence < self.config.get("VOICE_CONFIDENCE_THRESHOLD", 0.7): # Use configured threshold
            self.say("I'm sorry, I didn't quite catch that. Could you repeat?")
            return

        text_lower = text.lower()

        # Command parsing BEFORE LLM
        if "wander" in text_lower or "walk around" in text_lower or "explore" in text_lower or "pace around" in text_lower:
            self.say("Okay, I'll wander around for a bit!")
            # Using example parameters; these could be configurable or adjusted
            self.queue_action(WalkRandomlyAction(self, interval=10, max_distance=7, duration=60)) 
            return
        elif "stop" in text_lower or "halt" in text_lower or "stop walking" in text_lower or "stay here" in text_lower:
            self.say("Okay, I'm stopping.")
            self.queue_action(StopMovingAction(self))
            return
        elif text_lower.startswith("use item "): # e.g., "use item key_north_door"
            try:
                entity_id = text.split(" ", 2)[2] # Get the part after "use item "
                if entity_id:
                    self.say(f"Alright, I'll try to use the {entity_id}.")
                    self.queue_action(UseItemAction(self, entity_id=entity_id, move_to_item=True))
                else:
                    self.say("Which item should I use? Please say 'use item' followed by the item's name.")
            except IndexError:
                 self.say("Please tell me which item to use, like 'use item shiny key'.")
            return
        elif "drop it" in text_lower or "release item" in text_lower or "stop using that" in text_lower:
            self.say("Okay, I'll let go of it.")
            self.queue_action(UnuseItemAction(self))
            return
        
        # If no specific command, proceed to LLM or rule-based
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
        Called when a player is nearby (event from Hyperfy, e.g. specific trigger volume).
        This is different from the proactive check.
        """
        player_id = data.get("player_id", "unknown")
        distance = data.get("distance", 0.0)
        current_time = time.time()

        # Greet the player if they're close enough AND haven't been greeted recently
        # This specific event might be for closer proximity than proactive check.
        if distance < 3.0 and (player_id not in self.greeted_players_today or \
                               current_time - self.greeted_players_today[player_id] > self.greeting_cooldown):
            if random.random() < 0.6: # Higher chance to greet on this specific event
                self.say(f"Oh, hello there! So glad you could join this part of Wonderland!")
                self.greeted_players_today[player_id] = current_time
    
    def _proactive_greeting_check(self, current_time: float):
        """
        Periodically checks for nearby players and greets them if appropriate.
        """
        if not self.world_state:
            return

        players = self.world_state.get_objects_by_type("player")
        if not players:
            return

        for player_info in players: # Assuming player_info is a dict or object with id and position
            player_id = player_info.get("id") if isinstance(player_info, dict) else getattr(player_info, "id", None)
            player_position = player_info.get("position") if isinstance(player_info, dict) else getattr(player_info, "position", None)

            if not player_id or not player_position:
                continue

            if player_id == self.name: # Don't greet self
                continue

            # Calculate distance (assuming 3D positions [x, y, z])
            # This is a simplified distance calculation; a math.sqrt would be more accurate for Euclidean distance.
            # For performance, often squared distance is used if exact distance isn't critical.
            # dx = self.position[0] - player_position[0]
            # dy = self.position[1] - player_position[1] # If Y matters
            # dz = self.position[2] - player_position[2]
            # distance_sq = dx*dx + dz*dz # Assuming primarily ground plane distance matters
            # For now, using a helper if available, or simple diff
            # This part needs robust distance calculation. Assuming self.position and player_position are available
            # and are lists/tuples [x,y,z].
            try:
                dist = sum((a - b) ** 2 for a, b in zip(self.position, player_position))**0.5
            except (TypeError, IndexError) as e:
                self.logger.debug(f"Could not calculate distance to player {player_id}: {e}")
                continue


            if 5.0 < dist < 10.0: # Adjusted range for proactive greeting
                if player_id not in self.greeted_players_today or \
                   current_time - self.greeted_players_today[player_id] > self.greeting_cooldown:
                    
                    self.say("Hi there! Exploring Wonderland? Let me know if you need any help or have questions!")
                    self.greeted_players_today[player_id] = current_time
                    self.logger.info(f"Proactively greeted player {player_id} at distance {dist:.2f}m.")
                    # Optional: Break after one greeting per cycle to avoid multiple greetings at once
                    # break 

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
            You can help users find things, understand how the world works, or just chat.
            If you don't know something, it's okay to say so in a whimsical way.
            
            Current environment: Wonderland with a rabbit hole, looking glass, mushrooms, and a tea party area.
            Common things users might ask about: finding the White Rabbit, the Mad Hatter's tea party,
            the Queen of Hearts' castle, or how to change size (though you can't directly help with that).
            
            Human: {human_input}
            Alice:
            """
            
            prompt = PromptTemplate(
                input_variables=["personality", "human_input"],
                template=template
            )
            
            # Create the language model
            model_name = self.config.get("LANGCHAIN_MODEL", "gpt-3.5-turbo") # Get from config
            llm = OpenAI(model_name=model_name, temperature=0.7, max_tokens=150)
            
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
