# Smart College AI Assistant

## Project Overview

Smart College AI Assistant is a hackathon project built for students who waste time searching through scattered notes, PDFs, and academic material. The idea is to create an AI-powered study workspace where a student can upload notes or PDFs, ask questions from them, and instantly generate revision tools like flashcards and quizzes. This project fits the hackathon theme of **AI Automation & Intelligent Agents**, especially the **AI Knowledge Assistant** use case in **Education**, where students struggle to find accurate information quickly because knowledge is fragmented [file:1].

Our goal is not to build a huge all-in-one college platform. Our goal is to build a focused, polished MVP where **one uploaded document becomes an interactive study system**.

---

## Problem Statement

Students usually have study material spread across class notes, PDFs, assignments, WhatsApp messages, and teacher-shared resources. Because of this, they spend too much time searching for the right answer instead of actually learning.

We are solving this by building an AI assistant that:
- understands uploaded academic material,
- answers student doubts from that material,
- generates flashcards for revision,
- generates quizzes for self-testing.

---

## Core Idea

A student uploads one or more study PDFs or notes into the app. The system processes the content and turns it into an interactive AI assistant. After upload, the student can:
1. Ask questions from the uploaded notes
2. Generate flashcards from the notes
3. Generate quizzes from the notes

This makes the app a smart learning assistant instead of just a file viewer or generic chatbot.

---

## MVP Scope

### Features included in MVP
- PDF / Notes upload
- Text extraction from uploaded study material
- Chat with uploaded notes
- Flashcard generation from uploaded notes
- Quiz generation from uploaded notes
- Clean dashboard/workspace UI

### Features not included in MVP
- Full study planner
- Full assignment writer
- Voice assistant
- Collaboration between multiple students
- Advanced analytics
- Mobile app version

We are intentionally keeping the MVP small so it feels complete, polished, and demo-ready.

---

## User Flow

1. User opens the app.
2. User uploads a PDF or notes.
3. The app extracts and processes the text.
4. The user sees three main actions:
   - Ask a doubt
   - Generate flashcards
   - Generate a quiz
5. The AI returns results based on the uploaded study material.
6. The user studies from the generated output.

---

## Main Screens

### 1. Dashboard / Home
Purpose:
- Welcome the user
- Show upload area
- Show recently uploaded notes
- Show quick action buttons

### 2. Chat Workspace
Purpose:
- Let students ask doubts from uploaded notes
- Show assistant responses
- Show which file or subject is active

### 3. Flashcards View
Purpose:
- Generate revision flashcards from notes
- Allow students to go card by card

### 4. Quiz View
Purpose:
- Generate quiz questions from uploaded notes
- Help students test their understanding

---

## Tech Direction

### Frontend
- React or Next.js
- Tailwind CSS
- Clean AI-assistant style UI

### Backend
- FastAPI preferred
- REST API endpoints for upload, chat, flashcards, and quiz generation

### AI / Processing
- PDF text extraction
- Chunking and retrieval from uploaded notes
- AI-generated answers grounded in uploaded content
- AI-generated flashcards
- AI-generated quizzes

### Storage
- Metadata for uploaded files
- Text chunks / vector store if retrieval is implemented
- Basic saved history if time permits

---

## Implementation Logic

### 1. File Upload
The user uploads notes or PDFs. The backend stores the file and extracts text from it.

### 2. Text Processing
The extracted text is cleaned and broken into manageable chunks so the assistant can search relevant parts of the notes quickly.

### 3. Question Answering
When the user asks a question, the system retrieves the most relevant sections from the uploaded material and uses AI to answer based on that material rather than answering generically.

### 4. Flashcard Generation
The system reads the notes and generates important concept-question-answer pairs for quick revision.

### 5. Quiz Generation
The system creates MCQs or short-answer questions from the uploaded material to help students test themselves.

---

## Team Members

### Sanskar
Role:
- Product lead
- Frontend lead
- Final integration lead
- UI/UX direction

Main responsibilities:
- Finalize product vision and scope
- Design the dashboard, chat workspace, flashcard screen, and quiz screen
- Build or supervise frontend implementation
- Connect frontend with backend APIs
- Ensure the final product feels clean, polished, and demo-ready

### Ansh
Role:
- Backend lead
- File processing and API lead

Main responsibilities:
- Set up backend project structure
- Create upload API
- Handle PDF/text extraction
- Build chat endpoint
- Build flashcard generation endpoint
- Build quiz generation endpoint
- Manage data flow between frontend and AI logic

### Krishna
Role:
- AI workflow, testing

Main responsibilities:
- Help define prompt flows for chat, flashcards, and quizzes
- Test whether answers are grounded in uploaded content
- Prepare sample PDFs / demo data
- Do bug testing and edge-case checking
- Help build presentation, pitch flow, and final demo script
- Maintain documentation and proof of work for GitHub

---

## Phase-Wise Work Division

## Phase 1: Planning and Scope Freeze
**Owner:** Sanskar  
**Support:** Ansh, Krishna

Tasks:
- Finalize project name
- Finalize problem statement
- Freeze MVP features
- Finalize user flow
- Finalize what will NOT be built

Output:
- Final project direction
- Clear development scope
- Shared understanding across team

---

## Phase 2: UI/UX and App Structure
**Owner:** Sanskar  
**Support:** Krishna

Tasks:
- Create page structure
- Design dashboard layout
- Design chat layout
- Design flashcards layout
- Design quiz layout
- Define reusable UI components

Output:
- Wireframes or initial UI
- Frontend structure ready for development

---

## Phase 3: Backend Foundation
**Owner:** Ansh  
**Support:** Sanskar

Tasks:
- Create backend folder structure
- Set up FastAPI server
- Create upload route
- Create basic API routes
- Set up request/response format

Output:
- Running backend server
- Base API structure

---

## Phase 4: Document Processing
**Owner:** Ansh  
**Support:** Krishna

Tasks:
- Parse PDF/text files
- Extract raw content
- Clean and segment text
- Prepare content for AI usage

Output:
- Reliable text extraction pipeline

---

## Phase 5: AI Features
**Chat feature**
- **Owner:** Ansh
- **Support:** Krishna

Tasks:
- Build question-answer flow
- Retrieve relevant note content
- Generate grounded responses

**Flashcard feature**
- **Owner:** Krishna
- **Support:** Ansh

Tasks:
- Define flashcard prompt logic
- Test quality of generated cards
- Improve usefulness and clarity

**Quiz feature**
- **Owner:** Krishna
- **Support:** Ansh

Tasks:
- Define quiz generation logic
- Generate MCQs / short-answer questions
- Improve difficulty and relevance

Output:
- Working AI features for demo

---

## Phase 6: Frontend Integration
**Owner:** Sanskar  
**Support:** Ansh

Tasks:
- Connect upload UI to backend
- Connect chat UI to backend
- Connect flashcard UI to backend
- Connect quiz UI to backend
- Add loading, error, and empty states

Output:
- End-to-end working product

---

## Phase 7: Testing and Polish
**Owner:** Krishna  
**Support:** Sanskar, Ansh

Tasks:
- Test the full user flow
- Check if answers come from uploaded material
- Test invalid uploads and broken states
- Improve UX details
- Prepare stable demo data

Output:
- More reliable and polished MVP

---

## Phase 8: Demo and Submission
**Owner:** Sanskar
**Support:** Krishna, Ansh

Tasks:
- Prepare final pitch flow
- Prepare demo script
- Prepare screenshots / GitHub README assets
- Prepare final repository cleanup
- Prepare submission notes

Output:
- Demo-ready build
- Submission-ready repository

---

## Suggested Folder Ownership

### Sanskar owns
- `frontend/`
- UI components
- pages
- styling
- frontend API integration
- final app assembly

### Ansh owns
- `backend/`
- API routes
- upload logic
- file parsing
- retrieval / AI backend logic

### Krishna owns
- `docs/`
- prompts
- testing notes
- demo script
- sample content
- QA checklist

---

## Suggested Repository Structure

```bash
smart-college-ai-assistant/
│
├── info.md
├── README.md
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── app/
│   ├── styles/
│   └── utils/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── uploads/
│
├── docs/
│   ├── prompts.md
│   ├── testing-checklist.md
│   ├── demo-script.md
│   └── architecture-notes.md
│
└── assets/
    ├── screenshots/
    └── demo-files/
```

---

## GitHub Collaboration Plan

### Branch strategy
- `main` → stable branch
- `dev` → integration branch
- `feature/frontend-ui` → Sanskar
- `feature/backend-api` → Ansh
- `feature/prompts-testing-docs` → Krishna

### Commit ownership
Each member should push commits for their own section so contribution history stays clear.

Examples:
- Sanskar: `build dashboard and chat layout`
- Ansh: `add pdf upload and extraction api`
- Krishna: `add flashcard prompt flow and testing docs`

### Pull request flow
1. Work on personal feature branch
2. Push commits regularly
3. Open PR into `dev`
4. Team reviews basic functionality
5. Merge into `dev`
6. Final tested version goes into `main`

This will help preserve proper credit for each member’s work.

---

## Documentation Rules

To keep the project understandable for Gemini, GitHub, and future team members:
- Write clear function names
- Keep files modular
- Add comments only where necessary
- Maintain `docs/` for prompts, testing, and architecture
- Update `README.md` as features are completed
- Avoid making everything depend on one large file

---

## How AI Assistants Should Understand This Project

Any AI coding assistant helping in this repo should understand that:

- This is a hackathon MVP.
- The project is focused on students.
- The product is an AI Knowledge Assistant.
- The core value is turning uploaded study material into an interactive study system.
- The MVP includes only upload, note-based chat, flashcards, and quizzes.
- The project should stay modular and manageable.
- UI should be clean, modern, and assistant-like.
- Backend should be simple, practical, and demo-ready.
- We prefer shipping a smaller polished product over a large unfinished one.

---

## Final One-Line Summary

Smart College AI Assistant is a focused AI-powered study workspace that lets students upload notes, ask questions from them, and generate flashcards and quizzes from the same material.

---

## Credits

Built by:
- Sanskar
- Ansh
- Krishna

Each team member contributes through separate ownership areas, commits, and documentation so that credit remains transparent on GitHub and in the final hackathon submission.