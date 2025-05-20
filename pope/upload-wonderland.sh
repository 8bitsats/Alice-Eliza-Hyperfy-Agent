#!/bin/bash

# Stop on errors
set -e

# Print commands
set -x

echo "Uploading Wonderland..."

# Change to wonderland directory
cd wonderland

# Check if nvm is available
if command -v nvm &> /dev/null; then
    echo "Using nvm to switch to Node.js 16..."
    # Use Node.js 16 which is more compatible with the native modules
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm use 16 || nvm install 16
elif command -v node &> /dev/null; then
    # Just check the node version
    NODE_VERSION=$(node -v)
    echo "Current Node.js version: $NODE_VERSION"
    echo "Warning: Using current Node.js version. If build fails, try using Node.js 16."
else
    echo "Node.js not found. Please install Node.js 16."
    exit 1
fi

# Install dependencies if needed
echo "Installing dependencies..."
npm install

# Run the upload command
npm run upload:wonderland

echo "Upload complete!"
