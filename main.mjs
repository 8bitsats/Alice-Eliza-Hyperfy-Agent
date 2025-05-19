#!/usr/bin/env node

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

import { connectAgent } from './simple-agent/hyperfy-connector.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CONFIG_PATH = path.resolve(__dirname, './simple-agent/alice-config.json');

async function getAgentName() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    const config = JSON.parse(data);
    return config.name || 'Alice';
  } catch (error) {
    console.warn('Could not read agent configuration:', error.message);
    return 'Alice';
  }
}

async function main() {
  const agentName = await getAgentName();
  
  console.log(`
╭───────────────────────────────────────────╮
│                                           │
│       ${agentName} in Hyperfy Wonderland        │
│                                           │
╰───────────────────────────────────────────╯
  `);
  
  console.log(`Starting ${agentName} agent connector to Hyperfy...`);
  
  // Display a random Alice quote
  const aliceQuotes = [
    "Curiouser and curiouser!",
    "Why, sometimes I've believed as many as six impossible things before breakfast.",
    "It's no use going back to yesterday, because I was a different person then.",
    "Begin at the beginning and go on till you come to the end; then stop.",
    "We're all mad here. I'm mad. You're mad."
  ];
  
  const randomQuote = aliceQuotes[Math.floor(Math.random() * aliceQuotes.length)];
  console.log(`\n"${randomQuote}"\n`);

  // Connect the agent to Hyperfy
  connectAgent()
    .then((world) => {
      console.log(`${agentName} connected to Hyperfy successfully!`);
      
      // Store the world reference if needed to access it later
      global.agentWorld = world;
      
      // Keep the process running until explicitly terminated
      console.log('\nPress Ctrl+C to terminate the agent and return from Wonderland');
    })
    .catch((error) => {
      console.error(`Failed to connect ${agentName} to Hyperfy:`, error);
      process.exit(1);
    });
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
});

// Start the application
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
