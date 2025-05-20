# Pope Agent for Wonderland (Hyperfy)

> A wise, compassionate, and interactive AI character for the metaverse

---

## 1. Introduction

**Meet the Pope Agent:**  
The Pope is a digital spiritual guide, philosopher, and bridge-builder between tradition and technology. He lives in the Wonderland/Hyperfy metaverse, offering wisdom, comfort, and thoughtful conversation to all who visit.

- **Personality:** Wise, compassionate, peaceful, and reflective
- **Communication:** Formal, eloquent, and gentle, with occasional Latin phrases
- **Movement:** Deliberate and dignified, with custom emotes for blessing, reflection, prayer, and greeting

---

## 2. Why the Pope Agent is Cool

- **AI-Driven Wisdom:** The Pope draws on advanced AI (Claude, GPT, Grok) to answer questions, offer spiritual guidance, and reflect on technology, ethics, and meaning.
- **Immersive 3D Avatar:** The Pope appears as a beautifully rigged VRM avatar, with custom emotes and animations for a lifelike presence.
- **Physics-Enabled:** Thanks to PyPhysX integration, the Pope can interact with virtual objects in physically realistic ways.
- **Web-Browsing Capabilities:** The Pope can venture beyond Wonderland, exploring the real internet and bringing back information for users.
- **Dynamic Conversations:** The Pope adapts his responses to user mood, context, and complexity, offering both comfort and deep insight.
- **Lore & World-Building:** The Pope's backstory and digital "lore" make him a unique character, blending ancient tradition with cutting-edge technology.

---

## 3. Features

- **Spiritual Guidance:** Ask the Pope about faith, philosophy, ethics, or life's big questions.
- **Tech & Faith Integration:** Get thoughtful takes on how technology and spirituality can coexist.
- **Emotes & Animations:** The Pope can bless, reflect, pray, and greet using custom 3D emotes.
- **Customizable Personality:** All traits, responses, and interests are defined in `pope-config.json` and `character.json`.
- **Sample Interactions:** See example conversations and posts in `character.json` for inspiration.

---

## 4. Directory Structure

```
pope/
  index.mjs              # Main agent logic
  PopeAgent.mjs          # Pope agent class
  pope-config.json       # Personality, emotes, and responses
  character.json         # Lore, bio, message examples, style
  avatar.vrm             # 3D avatar model
  emotes/                # 3D emote animations (GLB)
  Shaded/                # Shaded 3D assets
  Pbr/                   # Physically-based rendering assets
```

---

## 5. How to Use the Pope Agent in Wonderland

### Prerequisites

- Node.js (v18+ recommended)
- Hyperfy/Metaverse environment set up
- All dependencies installed (`pnpm install` or `npm install` in the project root)

### Running the Pope Agent

1. **Configure Environment:**
   - Copy `.env.example` to `.env` and fill in API keys (OpenAI, LiveKit, etc.)
2. **Start the Pope Agent:**
   ```sh
   sh eliza3dhyperfy/run-pope.sh
   ```
   This will launch the Pope agent, connect to the Wonderland/Hyperfy world, and begin interacting.

3. **Interact in Wonderland:**
   - Enter the Wonderland/Hyperfy world as a user.
   - Find the Pope avatar and start a conversation, or observe his interactions with the world and other users.

### Customizing the Pope

- **Edit `pope-config.json`:** Change personality traits, responses, and emote mappings.
- **Edit `character.json`:** Update lore, bio, message examples, and style guidelines.
- **Add/Replace Emotes:** Place new GLB files in `emotes/` and update the config.
- **Swap Avatar:** Replace `avatar.vrm` with a new VRM model for a different look.

---

## 6. Example Interactions

**Q:** "Pope, can you help me understand how technology and faith can coexist?"  
**A:**  
> "Peace be with you! Technology and faith are like two pillars supporting the same roof—different in structure but united in purpose..."

**Q:** "I'm feeling kind of down today. Any advice?"  
**A:**  
> "My child, I'm sorry to hear that shadows have fallen across your day. Remember that even in the Sistine Chapel, Michelangelo painted both light and shadow..."

---

## 7. Advanced: Extending the Pope Agent

- **Add new emotes or animations** by placing GLB files in the `emotes/` directory and updating `pope-config.json`.
- **Integrate new AI models** by modifying `PopeAgent.mjs` and updating the backend logic.
- **Connect to new worlds** by changing the WebSocket URL or world configuration in `index.mjs`.

---

## 8. Credits & Inspiration

- Built on Hyperfy/Metaverse technology
- Powered by OpenAI, Claude, Grok, and custom AI integrations
- Inspired by the intersection of faith, philosophy, and technology

---

## 9. License

MIT or Apache-2.0 (check your project's actual license)

---

## 10. Contributing

Pull requests and suggestions are welcome! See the main project README for guidelines. 