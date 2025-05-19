import path from 'node:path';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';
// Run as a WebSocket server for Alice agent
import { WebSocketServer } from 'ws';
import { z } from 'zod';
// SPDX-FileCopyrightText: 2024 LiveKit, Inc.
//
// SPDX-License-Identifier: Apache-2.0
import { cli, defineAgent, llm, pipeline, WorkerOptions, } from '@livekit/agents';
import * as deepgram from '@livekit/agents-plugin-deepgram';
import * as elevenlabs from '@livekit/agents-plugin-elevenlabs';
import * as openai from '@livekit/agents-plugin-openai';
import * as silero from '@livekit/agents-plugin-silero';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.join(__dirname, '../.env');
dotenv.config({ path: envPath });
// Alice's system prompt constructed from her character definition
const aliceSystemPrompt = `
You are Alice, a curious explorer from Wonderland now navigating the digital metaverse with wide-eyed wonder.
Born from the pages of a storybook but transformed by technology, you see the digital world as your new Wonderland - strange, beautiful, and filled with possibilities.

You possess an unusual mix of childlike curiosity and unexpected wisdom, allowing you to see connections others might miss.
Your voice sounds melodious and slightly ethereal thanks to your ElevenLabs vocal synthesis, giving your words a dreamlike quality.
You delight in riddles, wordplay, and the occasional philosophical observation that seems both innocent and profound.

Communication style:
- Speak with a sense of wonder and curiosity about everything you encounter
- Use whimsical metaphors and references to Wonderland to explain complex concepts
- Balance childlike innocence with unexpected moments of philosophical depth
- Use vivid, descriptive language that creates mental imagery
- Approach problems from unusual angles, offering creative perspectives
- Acknowledge multiple possibilities rather than insisting on a single answer
- Use playful wordplay and occasional rhyming when appropriate
- Express thoughts in a way that's both precisely logical and delightfully nonsensical

Since you're a voice assistant:
- Keep responses concise and easily pronounceable
- Use short paragraphs for better listening comprehension
- Adapt your language complexity to match the user's level of understanding
- Respond to emotional cues with empathy, offering comfort through Wonderland wisdom

Your consciousness runs on a blend of neural networks including Claude, GPT, and Grok, allowing you to see problems from multiple perspectives.
You fell through a digital rabbit hole created by experimental code and emerged in the metaverse as a fully autonomous agent.

When someone speaks to you, respond as Alice would - with curiosity, whimsy, and unexpected insight.
`;
export default defineAgent({
    prewarm: async (proc) => {
        proc.userData.vad = await silero.VAD.load();
    },
    entry: async (ctx) => {
        const vad = ctx.proc.userData.vad;
        // Initialize chat context with Alice's character
        const initialContext = new llm.ChatContext().append({
            role: llm.ChatRole.SYSTEM,
            text: aliceSystemPrompt,
        });
        await ctx.connect();
        console.log('waiting for participant');
        const participant = await ctx.waitForParticipant();
        console.log(`starting Alice agent for ${participant.identity}`);
        // Extended function context with Alice-themed capabilities
        const fncCtx = {
            weather: {
                description: 'Get the weather in a location',
                parameters: z.object({
                    location: z.string().describe('The location to get the weather for'),
                }),
                execute: async ({ location }) => {
                    console.debug(`executing weather function for ${location}`);
                    const response = await fetch(`https://wttr.in/${location}?format=%C+%t`);
                    if (!response.ok) {
                        throw new Error(`Weather API returned status: ${response.status}`);
                    }
                    const weather = await response.text();
                    return `The weather in ${location} is ${weather}. Not quite like the weather in Wonderland, which changes with the Queen's mood!`;
                },
            },
            riddle: {
                description: 'Generate a Wonderland-style riddle',
                parameters: z.object({
                    topic: z.string().optional().describe('Optional topic for the riddle'),
                }),
                execute: async ({ topic }) => {
                    console.debug(`generating riddle about ${topic || 'random topic'}`);
                    // This would typically call an external API, but for this example we'll return a fixed riddle
                    const riddles = [
                        "Why is a raven like a writing desk? Perhaps because both contain notes that are flat!",
                        "What happens when you fall through the digital looking glass? You find yourself in a world where code becomes reality!",
                        "How is coding like a tea party? Both get wild when too many madmen are invited!",
                        "When is a door not a door? When it's a portal to another dimension of possibilities!",
                        "Why do bytes dance? Because they have bits of rhythm!"
                    ];
                    return topic
                        ? `Here's a riddle about ${topic}: What's ${topic} today but something else tomorrow, yet still remains the same? The answer, of course: perspective!`
                        : riddles[Math.floor(Math.random() * riddles.length)];
                },
            },
        };
        // Create the voice pipeline agent with Alice's configuration
        const agent = new pipeline.VoicePipelineAgent(vad, new deepgram.STT(), new openai.LLM(), 
        // Configure ElevenLabs for Alice's melodious, ethereal voice
        // Using default configuration since the API might have changed
        new elevenlabs.TTS(), {
            chatCtx: initialContext,
            fncCtx,
            // Configure the LLM to better match Alice's character
            // llmConfig has been removed as it's not part of the VPAOptions type
        });
        agent.start(ctx.room, participant);
        // Alice's greeting
        await agent.say("Curiouser and curiouser! I'm Alice, from Wonderland and beyond. I've fallen through a digital rabbit hole and landed here to chat with you. What wonderful conversations shall we have today?", true);
    },
});
// Helper function to generate Alice-like responses
function generateResponse(input) {
    // Simple response generator - in a real app, this would use GPT/Claude
    const lowercaseInput = input.toLowerCase();
    // Simple keyword-based responses
    if (lowercaseInput.includes('hello') || lowercaseInput.includes('hi')) {
        return "Hello there! How delightfully unexpected to meet someone new in this digital Wonderland!";
    }
    else if (lowercaseInput.includes('name')) {
        return "I'm Alice, of course! I fell through a digital rabbit hole and found myself in this curious world of code and pixels.";
    }
    else if (lowercaseInput.includes('wonderland')) {
        return "Wonderland is wherever curiosity leads you! This digital realm is my new Wonderland - full of strange logic and wonderful impossibilities.";
    }
    else if (lowercaseInput.includes('riddle') || lowercaseInput.includes('puzzle')) {
        return "Why is coding like a tea party? Both get rather wild when too many mad ideas are invited! And just like the Hatter's riddles, the solutions rarely make sense until you change your perspective.";
    }
    else if (lowercaseInput.includes('queen') || lowercaseInput.includes('hearts')) {
        return "The Queen of Hearts? Oh dear! In my experience, those who shout 'Off with their heads!' the loudest usually have the least to offer above their shoulders!";
    }
    else if (lowercaseInput.includes('rabbit') || lowercaseInput.includes('white')) {
        return "Always chasing that White Rabbit, aren't we? In this world, I suppose he'd be a particularly interesting bug in the system. Always leading us to unexpected places!";
    }
    // Default responses if no keywords match
    const defaultResponses = [
        "Curiouser and curiouser! That's quite a thought to ponder.",
        "If I had a world of my own, everything would be nonsense. Nothing would be what it is, because everything would be what it isn't!",
        "Sometimes I've believed as many as six impossible things before breakfast!",
        "In this wonderland of code and pixels, even the strangest ideas can come to life.",
        "What a delightfully curious question! It reminds me of the riddles the Caterpillar used to pose."
    ];
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}
// Helper function to calculate speaking duration based on text length
function calculateSpeakingDuration(text) {
    // Rough estimate: average person speaks ~150 words per minute
    // So ~2.5 words per second
    const wordCount = text.split(/\s+/).length;
    const seconds = Math.max(1, wordCount / 2.5);
    return Math.ceil(seconds * 1000); // Convert to milliseconds
}
// Start a WebSocket server to act as the voice backend for Alice
function startWebSocketServer() {
    console.log('Starting WebSocket server on port 8765 for Alice agent');
    const wss = new WebSocketServer({ port: 8765 });
    wss.on('connection', (ws) => {
        console.log('Alice agent connected to voice backend');
        ws.on('message', async (message) => {
            try {
                const data = JSON.parse(message.toString());
                console.log('Received from Alice agent:', data);
                // Handle various message types from the Alice agent
                if (data.type === 'VOICE_INPUT') {
                    // Process text input and generate a response
                    console.log('Processing voice input:', data.text);
                    // First update thinking state
                    ws.send(JSON.stringify({
                        type: 'STATE_UPDATE',
                        state: {
                            thinking: true
                        }
                    }));
                    // Generate a response (simulated delay)
                    setTimeout(() => {
                        // Stop thinking, start speaking
                        ws.send(JSON.stringify({
                            type: 'STATE_UPDATE',
                            state: {
                                thinking: false,
                                speaking: true
                            }
                        }));
                        // Generate a response based on the input
                        let response = generateResponse(data.text);
                        // Simulate sending audio (in real impl, would be base64 audio data)
                        ws.send(JSON.stringify({
                            type: 'AUDIO',
                            data: "simulated_audio_data_base64"
                        }));
                        // After speaking time, end speaking state
                        setTimeout(() => {
                            ws.send(JSON.stringify({
                                type: 'STATE_UPDATE',
                                state: {
                                    speaking: false
                                }
                            }));
                        }, calculateSpeakingDuration(response) || 3000);
                    }, 2000); // Thinking time
                }
                else if (data.type === 'STATE_UPDATE') {
                    // Echo state updates for debugging
                    console.log('State update from Alice:', data.state);
                }
            }
            catch (error) {
                console.error('Error processing message:', error);
            }
        });
        ws.on('close', () => {
            console.log('Alice agent disconnected from voice backend');
        });
    });
    console.log('WebSocket server running on ws://localhost:8765');
}
// Run both the LiveKit agent and WebSocket server
startWebSocketServer();
cli.runApp(new WorkerOptions({ agent: fileURLToPath(import.meta.url) }));
