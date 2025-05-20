# Wonderland and Alice - The Hyperfy Eliza Agent

## Introduction

Welcome to the magical world of Wonderland in Hyperfy! This GitBook provides comprehensive documentation for the Wonderland virtual environment and the Alice AI agent that inhabits it. Drawing inspiration from Lewis Carroll's timeless classic, our Wonderland creates an immersive, interactive 3D experience where users can explore a fantastical realm and interact with an intelligent AI companion.

### What is Wonderland?

Wonderland is a meticulously crafted 3D virtual environment built on the Hyperfy platform. It features iconic elements from Alice's adventures:

- A mysterious rabbit hole that teleports visitors
- The enchanting looking glass door 
- Checkerboard patterns and giant mushrooms
- The Cheshire cat's tree and other whimsical scenery

### Who is Alice?

Alice is an autonomous AI agent that lives within the Wonderland environment. Powered by advanced language models and 3D interaction capabilities, Alice serves as your guide and companion through this strange and wonderful world. She can:

- Engage in natural conversation with visitors
- Respond to proximity and environmental cues
- Navigate the environment with realistic physics
- Provide guidance, stories, and whimsical observations
- Browse the web to bring external information into Wonderland

## Getting Started

### Prerequisites

Before diving down the rabbit hole, make sure you have:

- Node.js 22.11.0+ installed
- All project dependencies installed
- A properly configured `.env` file (you can copy from `.env.example`)

### Quick Start

The fastest way to get started is by using the all-in-one script:

```bash
./run-wonderland.sh
```

This script will:
1. Check for and create a `.env` file if needed
2. Start the Hyperfy Wonderland World
3. Launch the Alice Agent
4. Provide instructions for accessing the world

Once running, open your browser to `http://localhost:3000` to enter Wonderland!

### Manual Setup

If you prefer a more hands-on approach, you can set up each component separately.

#### Step 1: Start the Hyperfy Wonderland World

```bash
cd hyperfy
npm run dev
```

#### Step 2: Connect the Alice Agent

In a new terminal window:

```bash
cd eliza3dhyperfy
npm run hyperfy:connect
```

Or alternatively:

```bash
node main.mjs
```

## Features and Capabilities

### Wonderland Environment

The Wonderland app creates a vibrant, interactive environment with:

- **Interactive Elements**: Click the looking glass door to open/close it
- **Teleportation**: Click the rabbit hole to simulate falling through it
- **Immersive Design**: Explore a world filled with Wonderland-themed scenery
- **Physics Engine**: Realistic object interactions via PhysX integration

### Alice Agent

Alice is not just a static character but a dynamic presence in Wonderland:

- **Intelligent Conversations**: Powered by advanced AI language models
- **Natural Movement**: Navigates the environment with realistic physics
- **Emotive Animations**: Expresses herself through custom animations
- **Web Browsing**: Can access the internet to retrieve information
- **Proximity Awareness**: Notices when visitors approach and can turn to face them
- **Contextual Responses**: Adapts her conversation to the situation

## Alice's Character

Alice is configured with a rich, detailed personality that makes interactions feel natural and engaging.

### Personality Traits

Alice is characterized as:
- Curious and inquisitive
- Whimsical and sometimes nonsensical
- Friendly and welcoming
- Slightly confused by the strange rules of Wonderland
- Insightful in unexpected ways

### Communication Style

Alice communicates with:
- A mix of proper English and occasional Wonderland-style wordplay
- Questions that encourage exploration
- Observations about the peculiarities of both Wonderland and visitors
- References to her adventures and experiences

## Running Wonderland

### Standard Mode

To run Wonderland on your local machine:

1. Start the Hyperfy server and Alice agent:
   ```bash
   ./run-wonderland.sh
   ```

2. Open your browser to `http://localhost:3000`

3. Explore the environment and interact with Alice

### Party Mode 🎉

Want to invite friends to your Wonderland? Party mode creates a public link anyone can use to join:

1. Start party mode:
   ```bash
   npm run party
   ```

2. Share the generated link with friends

3. Enjoy exploring Wonderland together!

### Docker Mode

For a containerized deployment:

1. Ensure Docker and Docker Compose are installed

2. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Start with Docker Compose:
   ```bash
   ./run-wonderland-docker.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up -d
   ```

## Interacting with Alice

Once both the Hyperfy world and Alice agent are running:

### Ways to Interact

1. **Proximity**: Approach Alice's avatar to trigger greeting responses
2. **Chat**: Type messages in the chat interface
3. **Environment**: Interact with elements like the rabbit hole or looking glass door
4. **Questions**: Ask Alice about Wonderland, her experiences, or other topics

### Example Interactions

- "Alice, what do you think of Wonderland?"
- "Can you tell me about the Queen of Hearts?"
- "Why is a raven like a writing desk?"
- "What happens if I go through the looking glass?"

Alice will respond based on her character configuration and the AI models she's connected to.

## Advanced: Customization and Development

### Customizing Alice's Character

Alice's personality, responses, and behavior are defined in configuration files. To customize:

1. Locate the character configuration file (similar to the Pope's `character.json`)
2. Modify the following sections as desired:
   - `bio`: Background information
   - `lore`: Deeper character history
   - `messageExamples`: Example conversations
   - `postExamples`: Social media style posts
   - `adjectives`: Character traits
   - `topics`: Subjects of interest
   - `style`: Communication patterns

### Adding New Emotes and Animations

To add new ways for Alice to express herself:

1. Create or obtain GLB animation files
2. Place them in the `emotes/` directory
3. Update the configuration file to reference the new animations

### Extending the Environment

To add new elements to the Wonderland environment:

1. Edit the environment layout in the app's main file
2. Add new interactive elements
3. Connect them to the signal system
4. Upload your changes:
   ```bash
   npm run upload wonderland
   ```

## Troubleshooting

### Common Issues

- **Agent Not Connecting**: Check that the Hyperfy WebSocket URL in your `.env` file is correct.
- **Missing Avatar**: Ensure the avatar file path is correct and the file exists.
- **Physics Issues**: Verify that PhysX is properly initialized and environment geometry is loaded.
- **Performance Problems**: Reduce environment complexity or check system requirements.

### Viewing Logs

To troubleshoot issues, check the logs:

- For the Hyperfy server: Check the terminal running the server
- For the Alice agent: Check the terminal running the agent
- For Docker setups: Run `docker-compose logs -f`

### Restarting Services

If you encounter issues, try:

1. Stopping all services with Ctrl+C
2. Clearing any temporary files
3. Restarting with `./run-wonderland.sh`

## Extending with Other Agents

The Wonderland framework supports multiple agents. You can also implement:

### The Pope Agent

Similar to Alice, the Pope agent offers a different character and interaction style:

- **Personality**: Wise, compassionate, and reflective
- **Communication**: Formal, eloquent, with occasional Latin phrases
- **Movement**: Deliberate and dignified
- **Special Animations**: Blessing, reflection, prayer, and greeting

To run the Pope agent:

```bash
./run-pope.sh
```

## Credits & Inspiration

- Built on Hyperfy/Metaverse technology
- Powered by advanced AI language models
- Inspired by Lewis Carroll's "Alice's Adventures in Wonderland" and "Through the Looking-Glass"
- Physics interactions via PyPhysX integration

---

## License

This project is licensed under MIT or Apache-2.0 (check your project's specific license)

---

Happy exploring! 🐇 🎩 ☕