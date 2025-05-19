# Hyperfy Agent Python Starter Kit

## Overview

This is a Python starter kit for building Hyperfy agents with capabilities similar to the Eliza TypeScript implementation. It provides a framework for creating interactive agents with voice capabilities, world state management, action systems, and physics simulation.

Designed for the upcoming agent PVP challenge, this starter kit enables anyone to build Hyperfy agents using Langchain or raw Python.

## Features

- **Voice Capabilities**: Speech recognition and text-to-speech for natural interactions
- **World State Management**: Track objects, players, and environment state
- **Action System**: Prioritized, queueable actions for agent behaviors
- **Physics Integration**: Physics simulation using PyPhysX for realistic agent movement
- **LangChain Integration**: Optional integration with LangChain for AI-powered responses

## Architecture

The starter kit is organized into several components:

- **Core**: Base agent class and core systems (world state, action system)
- **Voice**: Voice recognition and synthesis capabilities
- **Physics**: Physics simulation and movement actions
- **Agents**: Example agent implementations (Alice)

## Requirements

```
pygame==2.5.0
numpy==1.24.3
pillowcase==2.0.0
python-dotenv==1.0.0
langchain==0.0.267
pyphysx==0.2.5
speech_recognition==3.10.0
pyttsx3==2.90
requests==2.31.0
pydantic==2.0.3
pyaudio==0.2.13
json5==0.9.14
```

## Installation

1. Clone the repository or copy the files to your project directory

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. If using the language model integration, set your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Running the Alice Agent

```bash
python main.py --agent alice
```

Options:
- `--agent`, `-a`: Agent type (default: alice)
- `--config`, `-c`: Path to custom config file
- `--log-level`, `-l`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Creating Your Own Agent

1. Create a new agent class that inherits from `AgentBase`

```python
from src.core.agent_base import AgentBase

class MyAgent(AgentBase):
    def __init__(self, config):
        super().__init__("MyAgent", config)
        # Custom initialization
        
    def on_start(self):
        # Called when the agent starts
        self.say("Hello, world!")
        
    def on_voice_input(self, text, confidence):
        # Handle voice input
        self.say(f"You said: {text}")
        
    def update(self, delta_time):
        # Called every frame
        pass
```

2. Register your agent in `main.py`

```python
from src.agents.my_agent import MyAgent

def create_agent(agent_type, config):
    if agent_type.lower() == "alice":
        return AliceAgent(config)
    elif agent_type.lower() == "myagent":
        return MyAgent(config)
    else:
        logger.error(f"Unknown agent type: {agent_type}")
        return None
```

3. Run your agent

```bash
python main.py --agent myagent
```

## Core Components

### Agent Base

The `AgentBase` class provides core functionality for all agents:

- Voice capabilities via `say()` method
- Event system via `emit_event()` and `register_event_handler()`
- Action system via `queue_action()`
- Movement via `move_to()`

### World State

The `WorldState` class tracks objects, players, and their properties in the virtual world:

- Add/remove objects and players
- Update object positions and properties
- Query objects by type or position
- Serialize/deserialize world state

### Action System

The `ActionSystem` class manages agent actions with priorities and queuing:

- Queue actions with priorities
- Cancel or clear action queue
- Hook into action lifecycle (pre/post execute, completion, etc.)

### Physics Engine

The `PhysicsEngine` class provides physics simulation using PyPhysX:

- Rigid body dynamics for agents
- Collision detection and handling
- Raycasting for sensing
- Apply forces and impulses to agents

## Examples

### Alice Agent

The `AliceAgent` class demonstrates how to create a character with personality:

- Rule-based and/or LLM-based responses
- Event handling for world interactions
- Physics integration for movement
- Idle behaviors and custom events

## Parity with Eliza TypeScript Implementation

This starter kit aims to provide feature parity with the [Eliza TypeScript implementation](https://github.com/elizaOS/eliza-3d-hyperfy-starter) while offering Python-specific advantages:

- **Same Core Features**: Voice, world state, actions, and physics
- **Python Ecosystem**: Easy integration with ML libraries like LangChain, PyTorch, etc.
- **Simplified API**: Streamlined API design while maintaining similar capabilities

## Contributing

Contributions are welcome! Feel free to extend this starter kit with additional features or improvements.

## License

MIT
