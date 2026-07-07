# 🎓 Smart College AI Assistant

Smart College AI Assistant is a great, AI-powered study workspace that converts flat study notes, slides, and PDFs into fully interactive, personalized learning environments. 

Rather than scrolling through pages of lectures, students upload documents into a single consolidated dashboard to unlock grounded Q&A chat, audio-enabled 3D flashcards, and automated self-test quizzes.

---

## ✨ Premium Features

*   **🧠 Note-Grounded Q&A (RAG Engine)**: Answers are generated strictly from the context of your uploaded notes. Every answer includes a page citation (e.g. `[Page 3]`) that coordinates with the source document.
*   **🎙️ Voice-to-Voice Doubt Assistant**: Speak your question out loud! The browser-native speech recognition transcribes and automatically submits your question, creating a hands-free learning flow.
*   **🔊 Audio Study Playback (TTS)**: Auditory learners can click the speaker icon next to any flashcard or AI reply to hear the text read out loud.
*   **🃏 3D Revision Flashcards**: Flips study concepts in 3D using CSS transform backface-visibility animations.
*   **📝 Auto-Graded Quizzes**: Multiple-choice testing with slide-down AI explanations explaining why correct options were selected.
*   **📊 Dynamic Progress Analytics**: Tracks doubts solved, flashcard views, and quiz score averages locally in the user's browser, starting at `0` and growing with real study activity.
*   **🔌 Zero-Crash Offline Fallback**: Runs full heuristics offline if no API keys are loaded, making it immediately testable by anyone.

---

## ⚙️ How to Configure AI Providers (Google Gemini & Groq)

This application supports Google Gemini (`gemini-1.5-flash`) and Groq (`llama3-8b-8192`) cloud models.

### Option A: Save Keys via the UI Settings (No Server Restart Needed!) - **Recommended for Live Demos**
1. Launch the application and click **Account Settings** in the top-right profile dropdown menu.
2. Select your active provider (Google Gemini or Groq).
3. Paste your API Key in the corresponding **Google Gemini API Key** or **Groq API Key** input boxes
4. Click **Save Settings**.
   *   *Note*: Keys are saved securely in your browser's local storage and sent via encrypted headers, completely protecting them from being saved on the server database or git commits.

### Option B: Local Developer `.env` file
1. Copy the `.env.example` file in the root directory to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your keys (e.g., `GEMINI_API_KEY=AIzaSy...`).
3. Start or restart the FastAPI backend server to load the keys on boot.

---

## 🚀 How to Run the App Locally

The application uses a pure vanilla HTML5/CSS3/ES6 frontend shell and a lightweight FastAPI Python backend.

### Prerequisites
*   Python 3.10+
*   Install backend dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Command to Start
Run the following command from the project root directory:
```bash
python main.py
```
This will automatically launch the backend server on `http://127.0.0.1:8000` and open your default browser to start studying!

---

## 📂 Project Structure

```bash
college-ka-hackathon/
├── main.py                # System launcher (configures & boots uvicorn server)
├── README.md              # Project description & user guide
├── requirements.txt       # Python dependencies (FastAPI, PyPDF2)
├── info.md                # Hackathon overview & team roles
│
├── backend/               # FastAPI Backend Service
│   ├── main.py            # App routing definitions & static mount
│   ├── routes/            # REST endpoint routers (documents, ai, settings)
│   ├── services/          # Chunker, TF-IDF retriever, and AI wrappers
│   ├── schemas/           # Pydantic data validators
│   └── uploads/           # PDF storage directory
│
├── frontend/              # HTML5/CSS3/ES6 Frontend SPA Shell
│   ├── index.html         # Workspace main window
│   ├── style.css          # Premium dark aesthetics & 3D CSS animations
│   ├── components.js      # Modular rendering blocks (Dashboard, Flashcards, Quiz, Chat)
│   └── app.js             # SPA state coordinator and event triggers
│
└── docs/                  # Hackathon Submission Documents
    ├── presentation-slides.md  # PPT slide-by-slide presentation script
    ├── demo-script.md          # 3-minute video recording walkthrough script
    └── architecture-notes.md   # Grounding RAG & retrieval math details
```
