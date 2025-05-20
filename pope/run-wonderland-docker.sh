#!/bin/bash

# Script to run the Wonderland World and Alice Agent using Docker Compose

# Function to handle cleanup on exit
cleanup() {
  echo ""
  echo "Shutting down Docker containers..."
  docker-compose down
  exit 0
}

# Set up trap to catch exit and cleanup
trap cleanup SIGINT SIGTERM

# Check if .env file exists, create from example if not
if [ ! -f ".env" ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
  echo "Please edit .env file to configure your environment with appropriate API keys."
  echo "Press Enter to continue, or Ctrl+C to exit and edit the file."
  read
fi

# Check if shared directory exists
if [ ! -d "shared" ]; then
  echo "Creating shared directory..."
  mkdir -p shared
fi

# Check if character files are copied to shared directory
if [ ! -f "shared/alice_avatar.vrm" ]; then
  echo "Copying avatar file to shared directory..."
  cp simple-agent/avatar.vrm shared/alice_avatar.vrm
fi

if [ ! -f "shared/alice_character.json" ]; then
  echo "Copying character configuration to shared directory..."
  cp simple-agent/alice-config.json shared/alice_character.json
fi

# Build and start Docker containers
echo "Starting Wonderland World and Alice Agent containers..."
docker-compose up -d

echo ""
echo "✨ Wonderland World and Alice Agent containers are now running ✨"
echo ""
echo "► To view container logs: docker-compose logs -f"
echo "► To explore the Wonderland World: Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop all services and remove containers"

# Keep script running until user presses Ctrl+C
while true; do
  sleep 1
done
