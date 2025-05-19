# Python Wonderland

A Python implementation of the Alice in Wonderland-themed environment originally created for Hyperfy. This version uses Pygame to create a 2D interactive environment with similar features to the original 3D version.

## Features

- **Interactive Wonderland Environment**: A 2D world inspired by Lewis Carroll's classic tale
- **Animated Elements**: Spinning rabbit hole and interactive looking glass door
- **Checkerboard Pattern**: Classic Wonderland aesthetic
- **Giant Mushrooms & Cheshire Cat Tree**: Iconic elements from the story
- **Interactive Objects**: Click the looking glass door to open/close it, or click the rabbit hole to teleport

## Requirements

```
pygame==2.5.0
numpy==1.24.3
```

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

## Controls

- **Mouse Click**: Interact with elements in the environment
  - Click the blue door to open/close it
  - Click the black center of the rabbit hole to trigger the teleport action

## Implementation Details

- **Animation System**: Custom Tween class implementation based on the original JavaScript version
- **Interactive Elements**: Each element has its own class with update and draw methods
- **Game State Management**: Simple state management for tracking door status and time

## License

MIT
