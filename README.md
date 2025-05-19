# Alice in Hyperfy Wonderland

> *"Curiouser and curiouser!" cried Alice. "Now I'm exploring the metaverse!"*

## Bridging AI Personalities with 3D Virtual Worlds

Welcome to the GitBook guide for **Alice in Hyperfy Wonderland**, a revolutionary project that brings the beloved character of Alice from Lewis Carroll's classic tales into the immersive 3D environment of Hyperfy.

This guide documents our innovative approach to creating autonomous AI agents that exist beyond text interfaces, inhabiting virtual worlds with personality, movement, and interactive capabilities.

## What Makes This Project Innovative

The Alice in Hyperfy Wonderland project represents a significant leap forward in several key areas:

### 1. Embodied AI in Metaverse Environments

Traditional AI interactions happen through text or voice interfaces. Alice exists as a fully embodied character in a 3D space, capable of:

- Moving naturally through the environment
- Responding to proximity of other users
- Using animations and emotes for non-verbal communication
- Maintaining a consistent in-character personality

### 2. Multi-Modal Integration Architecture

We've developed a modular framework that combines:

- 3D avatar technology (VRM format)
- Real-time WebSocket communication
- Environmental awareness systems
- Character-driven AI responses
- Voice synthesis capabilities

This integration creates a fluid, believable presence that engages users on multiple sensory levels.

### 3. Extensible Character Framework

While our implementation focuses on Alice, the framework we've created can be used for any character or personality:

- Character configurations are separated from the core system
- Behavior patterns can be customized without code changes
- Animation sets can be swapped or expanded
- Multiple AI models can be integrated for different aspects of intelligence

### 4. Hyperfy Integration

By integrating directly with Hyperfy's node client, we've created one of the first examples of how AI characters can be deployed in existing metaverse platforms without extensive modifications.

## Contents of This Guide

This GitBook provides comprehensive documentation on:

- [System Architecture](architecture.md) - The technical foundations of the system
- [Character Development](character-development.md) - How Alice's personality was created
- [Integration Process](integration-process.md) - How we connected to Hyperfy
- [AI Backend Setup](ai-backend.md) - Creating the multi-model AI system
- [Voice Integration](voice-integration.md) - Adding ElevenLabs voice capabilities
- [Deployment Guide](deployment.md) - Running the complete system
- [Extension Guide](extending.md) - Creating your own characters

Each section includes code examples, configuration samples, and best practices learned through development.

## Getting Started
Wonderland x Alice x ElizaOS Hyperfy Agent
<p align="center">
  <img src="shared/assets/images/alice-banner.png" alt="Alice in Wonderland Hyperfy Agent" width="800">
</p>
A fully autonomous intelligent agent for Hyperfy virtual worlds, embodying Alice from Wonderland. This project integrates multi-model AI capabilities, web browsing, voice synthesis, and physics simulation to create an interactive and whimsical presence in your Hyperfy spaces.
✨ Features

🧠 Multi-Model Intelligence: Switch between Claude, GPT, and Grok models for different conversation styles
🌐 Browsing Capabilities: Web browsing via BrowserUse API integration
🔊 Voice Synthesis: Natural-sounding speech via ElevenLabs integration
⚙️ Physics Simulation: Realistic object interactions through PyPhysX
🎭 Character Embodiment: Fully realized Alice persona with consistent behavior and responses
🤝 Proximity Detection: Automatically greets and interacts with nearby users
📱 WebSocket Communication: Seamless connection between Python AI backend and Hyperfy frontend

🚀 Quick Start
Prerequisites

Docker and Docker Compose
A running Hyperfy server or access to Hyperfy worlds
API keys for: OpenAI, Anthropic, BrowserUse, and ElevenLabs

Installation

Clone the repository:
bashgit clone https://github.com/your-username/wonderland-alice-agent.git
cd wonderland-alice-agent

Set up environment variables:
bashcp .env.template .env
# Edit .env with your API keys and configuration

Start the services:
bashdocker-compose up -d

Connect to Hyperfy:
Alice will automatically connect to the specified Hyperfy WebSocket URL and appear in the world.

🔧 Configuration
The .env file contains several configuration options:
VariableDescriptionHYPERFY_WS_URLWebSocket URL for the Hyperfy worldAGENT_NAMEDisplay name for Alice in HyperfyOPENAI_API_KEYOpenAI API key for GPT modelANTHROPIC_API_KEYAnthropic API key for Claude modelXAI_API_KEYXAI API key for Grok model (optional)BROWSERUSE_API_KEYBrowserUse API key for web browsingELEVEN_LABS_API_KEYElevenLabs API key for voice synthesisDEBUGEnable/disable debug logging
📂 Project Structure
The project is organized into several components:

agent: JavaScript code for Hyperfy integration
backend: Python backend for AI, voice, and browsing capabilities
physics: Optional standalone physics simulation service
shared: Character definition, avatar, and assets

See Project-Structure.md for a detailed breakdown.
🧩 Components
Alice Agent (JavaScript)
The AliceAgent class connects to the Python backend and integrates with Hyperfy's systems. It handles:

Movement and animations in the 3D world
Proximity detection for nearby users
Chat message handling
WebSocket communication with the backend

ElizaOS Backend (Python)
The Python backend powers Alice's intelligence and capabilities:

Multi-Model AI: Claude, GPT-4, and Grok models for varied interaction styles
Voice Synthesis: ElevenLabs integration for natural speech
Web Browsing: BrowserUse API integration for information retrieval
Physics Simulation: PyPhysX integration for realistic object interactions

🎮 Interaction
Alice can interact with users in several ways:

Proximity Detection: Alice greets users who come near
Chat: Users can send messages in Hyperfy chat
Commands: Special commands for specific actions:

/model [name]: Switch AI model (e.g., /model claude, /model gpt)
/browse [url]: Browse the web for information
/voice [style]: Change voice style



🛠️ Development
Running Locally (Without Docker)
Backend:
bashcd backend
pip install -r requirements.txt
python alice_multimodel_agent.py
Agent:
bashcd agent
npm install
node hyperfy-connector.js
Customizing Alice
You can modify Alice's behavior by editing shared/alice_character.json. The character definition includes:

Biographical information
Conversation style
Example messages
Topics of interest
Personality traits

📄 License
MIT License
🙏 Acknowledgements

Hyperfy for the metaverse platform
LangChain for the AI framework
PyPhysX for physics simulation
ElevenLabs for voice synthesis
BrowserUse for browsing capabilities


To begin your journey with Alice in Hyperfy Wonderland, we recommend first understanding the [system architecture](architecture.md), then following our [quick start guide](quick-start.md) to get Alice running in your own Hyperfy environment.

> "Begin at the beginning," the King said, very gravely, "and go on till you come to the end: then stop."

Let's begin our adventure into the metaverse!
