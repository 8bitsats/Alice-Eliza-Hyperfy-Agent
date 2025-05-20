#!/bin/bash
set -e

# Onboarding setup script for Alice-Eliza-Hyperfy-Agent

copy_env() {
  local dir="$1"
  local example_file="$dir/.env.example"
  local env_file="$dir/.env"
  if [ -f "$example_file" ]; then
    if [ ! -f "$env_file" ]; then
      cp "$example_file" "$env_file"
      echo "  Copied $example_file to $env_file. Please fill in your secrets."
    else
      echo "  $env_file already exists. Skipping copy."
    fi
  else
    echo "  WARNING: $example_file not found. Please create it if needed."
  fi
}

echo "[0/4] Setting up environment files..."
copy_env "."
copy_env "AliceLiveKitVoice"
copy_env "pope"
copy_env "python/hyperfy_agent_python"
copy_env "python/python_wonderland"

echo "[1/4] Installing Node.js dependencies..."
if command -v pnpm &> /dev/null; then
  pnpm install
else
  npm install
fi

echo "[2/4] Building TypeScript scaffold (if any)..."
npx tsc --project tsconfig.build.json || true

echo "[3/4] (Optional) Python agent setup..."
if [ -d "python/hyperfy_agent_python" ]; then
  if command -v pip &> /dev/null; then
    echo "  Installing Python dependencies for python/hyperfy_agent_python..."
    pip install -r python/hyperfy_agent_python/requirements.txt || true
  else
    echo "  pip not found, skipping Python dependencies."
  fi
fi

echo "[4/4] (Optional) LiveKit Voice agent setup..."
if [ -d "AliceLiveKitVoice" ]; then
  cd AliceLiveKitVoice
  if command -v pnpm &> /dev/null; then
    pnpm install
  else
    npm install
  fi
  cd ..
fi

echo "\n---"
echo "Setup complete!"
echo "\nNext steps:"
echo "- Run the main Alice agent:     node main.mjs"
echo "- Run the TypeScript scaffold:  node dist/index.js (after editing src/index.ts)"
echo "- Run the Pope agent:           sh pope/run-pope.sh"
echo "- Run the Python agent:         cd python/hyperfy_agent_python && python main.py --agent alice"
echo "- Run the LiveKit Voice agent:  See AliceLiveKitVoice/README.md"
echo "\nSee the README.md for more details. Happy hacking!" 