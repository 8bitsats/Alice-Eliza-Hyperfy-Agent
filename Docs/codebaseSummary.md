# Alice in Hyperfy Wonderland - Codebase Summary

## Key Components and Their Interactions

This project integrates an AI agent (Alice) with the Hyperfy 3D virtual environment. Here's a breakdown of the core components:

### Entry Point
- **main.mjs** - The application entry point that initializes Alice and connects to Hyperfy

### Core Components
- **simple-agent/hyperfy-connector.mjs** - Main integration logic connecting Alice to Hyperfy
- **simple-agent/AliceAgent.mjs** - Alice's personality, behaviors, and communication
- **simple-agent/AgentLoader.js** - Custom asset loader for avatars and animations
- **simple-agent/AgentControls.js** - Movement and interaction controls for the agent

### Configuration Files
- **simple-agent/alice-config.json** - Alice's personality configuration
- **.env / .env.example** - Environment configuration for connections
- **docker-compose.yml** - Multi-container deployment configuration

### Documentation
- **README.md** - Project overview and setup instructions
- **cline_docs/** - Detailed documentation for various aspects of the project

## Data Flow

1. **Initialization Flow**
   - main.mjs loads configuration and initializes the connector
   - hyperfy-connector creates a world connection with custom components
   - AliceAgent is instantiated with the world reference
   - Character configuration is loaded from alice-config.json

2. **Communication Flow**
   - Hyperfy WebSocket ⟷ Agent Connector ⟷ AliceAgent
   - AliceAgent ⟷ (future) AI Backend Service
   - Proximity events → Character behaviors

3. **Interaction Flow**
   - Player proximity triggers onPlayerNearby()
   - Chat messages route through handleIncomingChat()
   - Animations and movement are controlled by AliceAgent

## External Dependencies

- **Hyperfy** - 3D virtual environment platform (`../hyperfy/build/world-node-client.js`)
- **Three.js** - 3D rendering engine (for avatar handling)
- **Node.js Modules** - ws, dotenv, fs/promises, path, url

## Recent Significant Changes

1. **Architecture Redesign**
   - Moved from a monolithic agent to a modular component system
   - Separated concerns between avatar loading, controls, and agent logic
   - Created a connector layer to manage the lifecycle and integration

2. **Alice Character Implementation**
   - Added Wonderland-themed personality with configurable traits
   - Implemented proximity-based interactions and idle behaviors
   - Created a character configuration system via JSON

3. **Documentation Improvements**
   - Added comprehensive documentation of the architecture
   - Created a project roadmap for future development
   - Added technical stack documentation and integration guides

4. **Deployment Configuration**
   - Added Docker and Docker Compose support
   - Created environment variable configuration via dotenv
   - Added npm scripts for easier execution

## User Feedback Integration

The system is designed to incorporate user feedback through:

1. **Character Configuration** - alice-config.json can be modified to adjust personality traits
2. **Environment Variables** - Connection settings can be customized in .env
3. **Docker Compose** - Service configuration can be adjusted for different deployment scenarios

Future improvements based on user feedback will focus on:
- Enhanced AI interactions via a dedicated backend service
- Voice synthesis for more natural communication
- Improved animation and movement behaviors
- Physics-based interactions with the environment

## Directory Structure

```
project-root/
├── main.mjs                  # Entry point
├── .env.example              # Example environment configuration
├── docker-compose.yml        # Docker deployment configuration
├── package.json              # Node.js package configuration
├── README.md                 # Project overview
├── cline_docs/               # Documentation files
│   ├── currentTask.md        # Current task description
│   ├── hyperfy-agent-connector.md # Connector documentation
│   ├── projectRoadmap.md     # Project roadmap and goals
│   ├── techStack.md          # Technology stack details
│   └── codebaseSummary.md    # This file - codebase overview
├── simple-agent/             # Agent implementation
│   ├── AgentControls.js      # Movement and interaction controls
│   ├── AgentLoader.js        # Asset loading system
│   ├── AliceAgent.mjs        # Alice agent implementation
│   ├── alice-config.json     # Alice personality configuration
│   ├── avatar.vrm            # Alice's 3D avatar model
│   └── hyperfy-connector.mjs # Hyperfy integration layer
└── hyperfy/                  # Hyperfy platform (external)
    └── build/                # Compiled Hyperfy client
        └── world-node-client.js # Hyperfy Node.js client API
