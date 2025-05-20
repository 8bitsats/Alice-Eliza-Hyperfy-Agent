#!/bin/bash

# Stop on errors
set -e

# Print commands
set -x

echo "Starting Pope agent..."

# Set NODE_ENV to development
export NODE_ENV=development

# Source the .env file if it exists
if [ -f .env ]; then
  echo "Loading environment from .env file"
  source .env
fi

# Create the node command
NODE_COMMAND="node --experimental-modules --no-warnings --es-module-specifier-resolution=node eliza3dhyperfy/pope/index.mjs"

# Run the command
echo "Running: $NODE_COMMAND"
$NODE_COMMAND
