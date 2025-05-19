# Alice in Wonderland Hyperfy Agent

A fully autonomous intelligent agent for Hyperfy virtual worlds that embodies Alice from Wonderland. This project seamlessly integrates multi-model AI capabilities, web browsing, voice synthesis, and physics simulation to create an interactive and enchanting presence in your Hyperfy metaverse spaces.

## ✨ Features

- **🧠 Multi-Model Intelligence**: Dynamically switch between Claude, GPT, and Grok models for versatile conversation styles
- **🌐 Web Capabilities**: Real-time information retrieval via BrowserUse API integration
- **🔊 Voice Synthesis**: Natural and expressive speech through ElevenLabs integration
- **⚙️ Physics Simulation**: Realistic environmental interactions powered by PyPhysX
- **🎭 Character Embodiment**: Authentic Alice persona with consistent behavior patterns
- **🤝 Proximity Awareness**: Intelligent detection and interaction with nearby users
- **📱 Seamless Communication**: Robust WebSocket connection between AI backend and Hyperfy frontend

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- A running Hyperfy server or access to Hyperfy worlds
- API keys for: OpenAI, Anthropic, BrowserUse, and ElevenLabs

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/wonderland-alice-agent.git
   cd wonderland-alice-agent
   ```

2. Configure environment variables:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` with your API keys and configuration settings

3. Launch the services:
   ```bash
   docker-compose up -d
   ```

4. Connect to Hyperfy:
   Alice will automatically connect to your specified Hyperfy WebSocket URL and appear in the world.

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `HYPERFY_WS_URL` | WebSocket URL for the Hyperfy world |
| `AGENT_NAME` | Display name for Alice in Hyperfy |
| `OPENAI_API_KEY` | OpenAI API key for GPT model |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude model |
| `XAI_API_KEY` | XAI API key for Grok model (optional) |
| `BROWSERUSE_API_KEY` | BrowserUse API key for web browsing |
| `ELEVEN_LABS_API_KEY` | ElevenLabs API key for voice synthesis |
| `DEBUG` | Enable/disable debug logging |

## 📂 Project Architecture

The project is structured into these primary components:

- **agent**: JavaScript code for Hyperfy integration
- **backend**: Python backend for AI, voice, and browsing capabilities
- **physics**: Optional standalone physics simulation service
- **shared**: Character definition, avatar assets, and configuration

*See `Project-Structure.md` for a detailed breakdown.*

## 🧩 Core Components

### Alice Agent (JavaScript)
The `AliceAgent` class connects to the Python backend and integrates with Hyperfy's systems to handle:
- Movement and animations in the 3D world
- Proximity detection for nearby users
- Chat message processing
- WebSocket communication with the backend

### ElizaOS Backend (Python)
The Python backend powers Alice's intelligence and capabilities through:
- **Multi-Model AI**: Claude, GPT-4, and Grok models for varied interaction styles
- **Voice Synthesis**: ElevenLabs integration for natural speech
- **Web Browsing**: BrowserUse API for information retrieval
- **Physics Simulation**: PyPhysX integration for realistic object interactions

## 🎮 Interaction Methods

Alice can interact with users in several intuitive ways:

- **Proximity Detection**: Automatically greets users who come within range
- **Chat**: Responds naturally to messages in Hyperfy chat
- **Commands**:
  - `/model [name]`: Switch AI model (e.g., `/model claude`, `/model gpt`)
  - `/browse [url]`: Browse the web for specific information
  - `/voice [style]`: Change voice characteristics and style

## 🛠️ Development

### Running Locally (Without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python alice_multimodel_agent.py
```

**Agent:**
```bash
cd agent
npm install
node hyperfy-connector.js
```

### Customizing Alice

You can modify Alice's behavior by editing `shared/alice_character.json`. The character definition includes:
- Biographical information
- Conversation style preferences
- Example dialogue patterns
- Topics of interest
- Personality traits

## 📄 License
MIT License

## 🙏 Acknowledgements
- Hyperfy for the metaverse platform
- LangChain for the AI framework
- PyPhysX for physics simulation
- ElevenLabs for voice synthesis
- BrowserUse for browsing capabilities

---

*"Begin at the beginning," the King said, very gravely, "and go on till you come to the end: then stop."*

Ready to begin your adventure into the metaverse with Alice as your guide!
