# Smart College AI Assistant - Frontend Workspace

This repository hosts the frontend UI shell for **Smart College AI Assistant**, an AI-powered study workspace that converts single documents (slides, notes, PDFs) into interactive learning systems. 

This project is built for the **AI Knowledge Assistant** hackathon theme.

---

## 🚀 How to Run the App

This app is built using zero-dependency, pure vanilla HTML5, CSS3, and ES6 Javascript. It requires no setup, compiling, or node_modules.

### Option 1: Run via Python Preview Server (Recommended)
From the root directory, run the following command in your terminal:
```bash
python main.py
```
This will launch a local HTTP server on port 8000 and automatically open your default browser to `http://localhost:8000`.

### Option 2: Open HTML Directly
You can open `frontend/index.html` directly in any web browser by double-clicking it on your file explorer.

---

## ⚙️ AI Provider Configuration

This application includes optional multi-provider AI support (Local Offline, Google Gemini, and Groq).

### Setup Instructions:
1. **Copy Environment Template**:
   Copy `.env.example` in the root directory to `.env`:
   ```bash
   cp .env.example .env
   ```
2. **Add API Keys**:
   Open `.env` and fill in your keys (e.g., `GEMINI_API_KEY` or `GROQ_API_KEY`).
3. **Change Provider in Settings**:
   Launch the app, click **Account Settings** in the top right menu, and select your provider.
4. **Out-of-the-box Ready**:
   If no keys are configured, the app automatically runs in **Local Mode (Offline Heuristics)** so judges can test it instantly without any setup.

---

## 📂 Repository Structure

The frontend code is structured as follows:

```bash
college-ka-hackathon/
├── main.py            # Zero-dependency Python server (serves static folder)
├── README.md          # Project instructions & walkthrough
├── info.md            # Technical context and team roles
└── frontend/          # Main frontend workspace files
    ├── index.html     # HTML SPA shell layout
    ├── style.css      # Premium dark-mode variables, 3D flip animations, and components
    ├── mockData.js    # Academic databases for default study courses (OS, ML, Chemistry)
    ├── components.js  # Modular render blocks (Dashboard, Upload, Chat, Cards, Quiz)
    └── app.js         # Core SPA controller, transitions, and state management
```

---

## 🎨 Design Features

- **Premium Dark Aesthetics**: Styled with deep slate variables (`#060913` base) and royal indigo-to-electric-blue gradients.
- **Workflow Reinforcement**: Visual focus on the cycle: **Upload Notes ➔ Chat/Ask Doubts ➔ Learn Flashcards ➔ Test Quiz**.
- **Interactive 3D Flashcards**: Flip cards dynamically in 3D using pure CSS transforms (`rotateY` on backface-hidden surfaces).
- **Interactive Quizzes**: Real-time option validation (correct/incorrect states) complete with slide-down AI Explanations and scoreboard metrics.
- **Mock Document Generator**: Supports drag-and-drop file uploads, simulating real-time file processing and parsing with progressive loading cues before populating the workspace context.
- **Dual-Panel Workspace**: View your processed document text side-by-side with the AI assistant chat thread, complete with citation links that scroll the reader to relevant sections.
