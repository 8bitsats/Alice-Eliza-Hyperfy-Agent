#!/bin/bash

# Script to run both the Hyperfy Wonderland World and the Alice Agent

# Function to handle cleanup on exit
cleanup() {
  echo ""
  echo "Shutting down Wonderland processes..."
  kill $HYPERFY_PID 2>/dev/null
  kill $ALICE_PID 2>/dev/null
  exit 0
}

# Set up trap to catch exit and cleanup
trap cleanup SIGINT SIGTERM

# Check if .env file exists, create from example if not
if [ ! -f ".env" ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
  echo "Please edit .env file to configure your environment."
  echo "Press Enter to continue with default settings, or Ctrl+C to exit and edit the file."
  read
fi

# Launch Hyperfy in the background
echo "Starting Hyperfy Wonderland World..."
cd hyperfy
npm run dev &
HYPERFY_PID=$!
cd ..

# Wait for Hyperfy to start up
echo "Waiting for Hyperfy to initialize (10 seconds)..."
sleep 10

# Launch Alice Agent
echo "Starting Alice Agent..."
npm run hyperfy:connect &
ALICE_PID=$!

# Alternatively, you can start the Eliza implementation directly:
# cd eliza
# npm run dev &
# ALICE_PID=$!
# cd ..

echo ""
echo "✨ Wonderland World and Alice Agent are now running ✨"
echo ""
echo "► To explore the Wonderland World: Open http://localhost:3000 in your browser"
echo "► Alice should appear as an avatar in the Wonderland environment"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to terminate with Ctrl+C
wait $HYPERFY_PID $ALICE_PID
