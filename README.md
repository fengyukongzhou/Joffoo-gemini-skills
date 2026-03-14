# Joffoo Gemini Skills

A collection of specialized **Gemini CLI Skills** designed to supercharge your Obsidian workflow and content management. These skills leverage AI for complex automation tasks, including high-quality web clipping, multilingual archiving, and structured content management.

## 🚀 Key Skills

### 1. [translate-archive](./translate-archive)
A powerful workflow for web clipping, high-precision AI translation, and automatic archiving into Obsidian.
- **Web Clipping**: Uses `defuddle-cli` (or `web_fetch` fallback) to extract clean markdown from URLs.
- **Three-Mode Translation**: Supports `quick`, `normal` (analyze + translate), and `refined` (analyze + translate + review + polish) modes.
- **Auto-Archiving**: Automatically adds YAML metadata and saves the final result to `03-Resources/`.
- **Glossary Support**: Supports custom glossaries via `EXTEND.md`.

### 2. [draft-to-weekly](./draft-to-weekly)
Streamlines the process of converting raw drafts into structured weekly articles or professional newsletters.
- **Structured Transformation**: Converts single drafts into a weekly magazine format.
- **AI-Powered Visualization**: Generates image prompts and handles image reconstruction for final output.

### 3. [rename-linked-images](./rename-linked-images)
A robust utility for batch renaming image attachments and updating internal markdown links.
- **Rule-Based Renaming**: Supports custom prefixes, date strings (MMDD, DDMM, YYMMDD), and automatic index padding.
- **Link Syncing**: Automatically updates WikiLinks (`![[...] ]`) and standard Markdown links in the document.
- **Format Conversion**: Includes a standalone script to convert between WikiLinks and Markdown image syntax.

## 🛠️ Requirements

To ensure all skills run correctly, make sure you have the following tools installed:
- **Bun**: Fast JavaScript runtime (recommended).
- **Node.js / npx**: For running TypeScript scripts.
- **defuddle-cli**: For web clipping functionality in `translate-archive`.
- **Python 3.x**: For running image management and weekly sync scripts.

## 📦 Installation

1. Navigate to your Gemini CLI skills directory (usually `.gemini/skills/`).
2. Clone this repository:
   ```bash
   git clone https://github.com/fengyukongzhou/Joffoo-gemini-skills.git
   ```
3. Activate a skill in Gemini CLI:
   ```javascript
   activate_skill(name='translate-archive')
   ```

## 📄 License

MIT License. Feel free to use and modify for your personal workflow.
