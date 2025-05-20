# Next Steps for Alice in Hyperfy Wonderland

This guide outlines what you can do next with your Alice in Hyperfy integration.

## Immediate Steps

### 1. Run Alice Locally

If you haven't already, run Alice to interact with a local Hyperfy instance:

```bash
# Start Alice agent
npm run hyperfy:connect
```

### 2. Setting Up the Complete Environment

To set up the complete environment with AI backend:

1. Create a `.env` file based on the `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to add your API keys:
   ```bash
   # At minimum, set these variables:
   HYPERFY_WS_URL=ws://localhost:3000/ws
   AGENT_NAME="Alice in Wonderland"
   ```

3. If you want to run with Docker Compose:
   ```bash
   # Create necessary directories
   mkdir -p backend physics shared

   # Copy your avatar.vrm to the shared directory
   cp simple-agent/avatar.vrm shared/alice_avatar.vrm
   
   # Copy your character configuration
   cp simple-agent/alice-config.json shared/alice_character.json
   
   # Start the services
   docker-compose up -d
   ```

## Extending Alice

### 1. Enhance Alice's Personality

Modify `simple-agent/alice-config.json` to adjust Alice's personality traits:

- Add more Wonderland quotes
- Customize greeting styles
- Adjust idle behavior frequencies

### 2. Create AI Backend (Python)

To create a dedicated AI backend for more advanced interaction:

1. Create a basic Python backend in the `backend` directory:

```python
# backend/alice_multimodel_agent.py
import asyncio
import websockets
import json
import os
import time
import random

# For OpenAI integration (optional)
# import openai

async def handler(websocket):
    print("Alice backend connected to agent")
    
    try:
        while True:
            # Receive message from agent
            message = await websocket.recv()
            data = json.loads(message)
            
            # Simple echo response for testing
            if data.get('type') == 'chat':
                user_message = data.get('message', '')
                user_name = data.get('user', 'someone')
                
                # Generate Alice response
                response = generate_alice_response(user_message, user_name)
                
                # Send response back to agent
                await websocket.send(json.dumps({
                    "type": "response",
                    "message": response
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

def generate_alice_response(message, user):
    # Simple rule-based response for testing
    # Replace with actual LLM call in production
    
    alice_phrases = [
        "Curiouser and curiouser!",
        "We're all mad here.",
        "It's no use going back to yesterday, because I was a different person then.",
        "If you don't know where you're going, any road will get you there.",
        "Why, sometimes I've believed as many as six impossible things before breakfast."
    ]
    
    # Add simple keyword matching
    if "hello" in message.lower() or "hi" in message.lower():
        return f"Hello there, {user}! Welcome to Wonderland!"
    
    if "who are you" in message.lower():
        return "I'm Alice, of course! Alice in Wonderland."
    
    if "wonderland" in message.lower():
        return "Yes, Wonderland is quite the curious place. " + random.choice(alice_phrases)
    
    # Default to a random Alice phrase
    return random.choice(alice_phrases)

async def main():
    # Get port from environment or use default
    port = int(os.environ.get("PORT", "8765"))
    
    print(f"Alice backend starting on port {port}")
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

2. Create a Dockerfile for the backend:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the WebSocket port
EXPOSE 8765

# Run the application
CMD ["python", "alice_multimodel_agent.py"]
```

3. Create a requirements.txt file:

```
# backend/requirements.txt
websockets==12.0
openai==1.3.0
```

### 3. Add Voice Capability

To add voice capability to Alice:

1. Create a basic voice server in the `backend` directory:

```python
# backend/alice_voice.py
import asyncio
import websockets
import json
import os
import requests
import io
import wave
import base64

# Elevenlabs API for voice synthesis
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

async def handler(websocket):
    print("Voice service connected")
    
    try:
        while True:
            # Receive message
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get('type') == 'tts':
                text = data.get('text', '')
                
                # Generate speech
                audio_data = generate_speech(text)
                
                # Send audio back
                await websocket.send(json.dumps({
                    "type": "audio",
                    "data": audio_data
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

def generate_speech(text):
    """Generate speech using ElevenLabs API"""
    if not ELEVENLABS_API_KEY:
        print("No ElevenLabs API key provided")
        return ""
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Convert to base64 for sending over WebSocket
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return audio_base64
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return ""
            
    except Exception as e:
        print(f"Exception: {e}")
        return ""

async def main():
    # Get port from environment or use default
    port = int(os.environ.get("VOICE_PORT", "8767"))
    
    print(f"Alice voice service starting on port {port}")
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

2. Add this service to your `docker-compose.yml` configuration.

### 4. Customize Alice's Avatar

To use a different VRM avatar for Alice:

1. Find or create a VRM file for Alice
2. Replace `simple-agent/avatar.vrm` with your new VRM file
3. Update the `alice-config.json` if necessary with new avatar specifications

### 5. Add More Emotes and Animations

To add more emotes and animations:

1. Add new animation files to the `emotes/` directory 
2. Update the `AliceAgent.mjs` file to include these new animations
3. Modify Alice's behavior to use these animations at appropriate times

## Deployment

For production deployment:

1. Set up your Hyperfy server
2. Configure the `.env` file with production settings
3. Deploy using Docker Compose
4. Set up SSL for secure WebSocket connections

## Troubleshooting

If you encounter issues:

1. Check the Hyperfy connection URL in `.env`
2. Verify avatar file exists and is a valid VRM
3. Check logs for any WebSocket connection errors
4. Verify that the Hyperfy server is running
5. Check that your backend services are running if you're using them

## Next Development Goals

Based on your project roadmap, consider focusing on:

1. Enhancing the AI backend with multi-model support
2. Adding voice synthesis and mouth animation
3. Implementing more complex environmental awareness
4. Creating a character selection system for multiple agents
