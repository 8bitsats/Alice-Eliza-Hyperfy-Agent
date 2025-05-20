# Configuration settings for Hyperfy Python Agent Kit

# Agent settings
AGENT_NAME = "Alice"
AGENT_VOICE_ID = "en-US-Neural2-F"  # Default voice ID
AGENT_PERSONALITY = "friendly, curious, whimsical"
AGENT_KNOWLEDGE_BASE = "alice_in_wonderland"

# Physics settings
PHYSICS_ENABLED = True
PHYSICS_TIMESTEP = 1/60  # 60 fps simulation
GRAVITY = [0, -9.81, 0]  # Standard gravity

# World settings
WORLD_SIZE = [100, 50, 100]  # x, y, z dimensions
WORLD_GROUND_ENABLED = True
WORLD_SKYBOX = "wonderland"

# Voice recognition settings
VOICE_RECOGNITION_ENABLED = True
VOICE_RECOGNITION_LANGUAGE = "en-US"
VOICE_CONFIDENCE_THRESHOLD = 0.7

# Action system settings
ACTION_COOLDOWN = 1.0  # Seconds between actions
ACTION_MAX_QUEUE = 5   # Maximum queued actions

# Networking settings
NETWORK_PORT = 8080
NETWORK_HOST = "localhost"
NETWORK_PROTOCOL = "websocket"

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "hyperfy_agent.log"

# Langchain settings
LANGCHAIN_ENABLED = True
LANGCHAIN_MODEL = "gpt-3.5-turbo"  # Default model
