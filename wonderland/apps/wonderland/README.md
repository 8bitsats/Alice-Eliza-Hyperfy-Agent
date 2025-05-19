# Wonderland App for Hyperfy

This app creates an Alice in Wonderland-themed environment for Eliza in Hyperfy.

## Features

- **Interactive Wonderland Environment**: A vibrant world inspired by Lewis Carroll's classic tale
- **Animated Elements**: Spinning rabbit hole and interactive looking glass door
- **Exploration Elements**: Checkerboard pattern, giant mushrooms, Cheshire cat's tree, and more
- **Interactive Objects**: Click the looking glass door to open/close it, or click the rabbit hole to teleport

## Installation

1. Ensure you're in the Wonderland app directory:
   ```
   cd wonderland/apps/wonderland
   ```

2. Upload the app to Hyperfy:
   ```
   npm run upload wonderland
   ```

3. In your Hyperfy world, press Tab to open the editor, click Add, and select the Wonderland app from the Uploads tab.

## Usage

### Interactive Elements

1. **Looking Glass Door**: Click on the blue mirror part of the looking glass to open or close the door.

2. **Rabbit Hole**: Click on the black hole in the center of the rabbit hole to teleport upward (simulating falling into the rabbit hole).

### Integration with Alice Agent

This Wonderland app is designed to work with the Alice in Wonderland-themed AI agent. The environment provides:

- Thematic spaces for Alice to inhabit
- Interactive elements that respond to user clicks
- Signal emitters that can communicate with other apps

## Development

To modify this app:

1. Edit the `index.js` file to change the environment layout or add new features
2. Test your changes with:
   ```
   npm run upload wonderland
   ```

### Events and Signals

The app emits the following signals:

- `RabbitHoleEntered`: When a player clicks on the rabbit hole and teleports
- Listens for `WonderlandEvent`: Generic event that can be sent by other apps

## License

This project is part of the Eliza 3D Hyperfy starter kit. See the main repository for licensing information.
