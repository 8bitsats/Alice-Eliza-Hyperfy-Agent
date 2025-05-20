# Alice-Eliza-Hyperfy-Agent

> *"Curiouser and curiouser!" cried Alice. "Now I'm exploring the metaverse!"*

---

## Getting Started as a New Developer

1. **Install dependencies:**
   ```sh
   npm install
   # or
   pnpm install
   ```

2. **Run the main Alice agent (JavaScript):**
   ```sh
   node main.mjs
   ```

3. **TypeScript migration workflow:**
   - Edit or add files in `src/` as `.ts` files.
   - Build TypeScript to JavaScript:
     ```sh
     npx tsc --project tsconfig.build.json
     # or
     npm run build:ts
     ```
   - Run the built JS (for example):
     ```sh
     node dist/index.js
     ```
   - As you migrate, port logic from `main.mjs` and `simple-agent/` into `src/`.

4. **Other agents:**
   - **Pope agent:** See `pope/README.md` and run with `sh pope/run-pope.sh`
   - **LiveKit voice agent:** See `AliceLiveKitVoice/README.md`
   - **Python agent:** See `python/hyperfy_agent_python/README.md`

---

## Overview

This monorepo brings together multiple advanced AI agents and supporting systems for the Hyperfy metaverse, including:

- **Alice Agent** (Node.js/TypeScript/JavaScript)
- **Pope Agent** (Node.js/JavaScript)
- **LiveKit Voice Agent** (Node.js/TypeScript)
- **Python Hyperfy Agent** (Python)
- **Wonderland Apps** (JavaScript)
- **Shared assets, emotes, and documentation**

---

## Project Structure

```
Alice-Eliza-Hyperfy-Agent/
│
├── main.mjs                # Main entry for Alice agent (Node.js)
├── src/                    # TypeScript migration entry (scaffolded)
├── simple-agent/           # Alice agent core logic (JavaScript)
├── pope/                   # Pope agent and assets
├── AliceLiveKitVoice/      # LiveKit voice pipeline agent (TypeScript)
├── python/                 # Python Hyperfy agent
├── wonderland/             # Wonderland apps and assets
├── emotes/                 # Shared emotes
├── Docs/                   # Project documentation
└── ...
```

---

## 1. Alice Agent (Node.js/TypeScript/JavaScript)

- **Entry:** `main.mjs`
- **Core logic:** `simple-agent/`
- **TypeScript migration:** `src/index.ts` (scaffolded, port logic here as you migrate)
- **Features:** Embodied AI, Hyperfy integration, emotes, personality, modular config

**Run Alice agent:**
```sh
node main.mjs
```

---

## 2. Pope Agent (`pope/`)

A wise, compassionate, and interactive AI character for the metaverse.

- **Entry:** `pope/index.mjs`
- **Agent class:** `pope/PopeAgent.mjs`
- **Config:** `pope/pope-config.json`, `pope/character.json`
- **Avatar:** `pope/avatar.vrm`
- **Emotes:** `pope/emotes/`
- **Docs:** `pope/README.md`, `pope/usage.md`, `pope/run-wonderland-guide.md`

**Run Pope agent:**
```sh
sh pope/run-pope.sh
```

**Customize:**  
Edit `pope-config.json` and `character.json` for personality, lore, and emotes.

---

## 3. LiveKit Voice Agent (`AliceLiveKitVoice/`)

A TypeScript-based voice pipeline agent using the [LiveKit Agents Framework](https://github.com/livekit/agents-js).

- **Entry:** `AliceLiveKitVoice/src/agent.ts`
- **Build:** `pnpm build` (or `npm run build`)
- **Run:** `node dist/agent.js dev`
- **Docs:** `AliceLiveKitVoice/README.md`

**Setup:**
1. Install dependencies: `pnpm install`
2. Configure `.env.local` with API keys (see `README.md`)
3. Build and run as above

---

## 4. Python Hyperfy Agent (`python/hyperfy_agent_python/`)

A Python starter kit for building Hyperfy agents with voice, world state, actions, and physics.

- **Entry:** `python/hyperfy_agent_python/main.py`
- **Agents:** `python/hyperfy_agent_python/src/agents/`
- **Docs:** `python/hyperfy_agent_python/README.md`

**Run Alice agent (Python):**
```sh
cd python/hyperfy_agent_python
pip install -r requirements.txt
python main.py --agent alice
```

**Create your own agent:**  
See the Python README for instructions on subclassing and registering new agents.

---

## 5. Wonderland Apps (`wonderland/`)

Contains apps and assets for the Wonderland/Hyperfy world.

- **Main app:** `wonderland/apps/wonderland/`
- **Treasure chest app:** `wonderland/apps/treasure-chest/`
- **Assets:** `wonderland/apps/wonderland/assets/`, `wonderland/apps/treasure-chest/assets/`

---

## 6. Documentation

- **Docs:** `Docs/` (architecture, innovation, codebase summary, tech stack, etc.)
- **Pope agent docs:** `pope/README.md`, `pope/usage.md`
- **Python agent docs:** `python/hyperfy_agent_python/README.md`
- **LiveKit voice agent docs:** `AliceLiveKitVoice/README.md`

---

## 7. TypeScript Migration

- The project is currently JavaScript-first for the main agent.
- A TypeScript scaffold is provided in `src/index.ts` and `tsconfig.json`.
- As you migrate, port logic from `main.mjs` and `simple-agent/` into `src/`.

---

## 8. Contributing

Pull requests and suggestions are welcome! See the contributing guidelines in each subproject and the main Docs.

---

## 9. License

See `LICENSE` in the root and in each subproject for details.
