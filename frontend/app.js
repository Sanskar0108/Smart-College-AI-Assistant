/**
 * Smart College AI Assistant - Core Frontend Application Controller
 * Manages SPA state, routes navigation, handles mock file processing,
 * triggers mock AI chat responses, and keeps track of flashcard/quiz sessions.
 */

class SmartCollegeApp {
  constructor() {
    this.state = {
      currentView: 'dashboard', // dashboard, upload, chat, flashcards, quiz
      activeDocumentId: null, // set dynamically from backend
      documents: [], // loaded dynamically from backend
      settings: {
        user_name: 'User',
        user_about: 'Active Student',
        model: 'local-heuristic',
        ollama_url: 'http://localhost:11434',
        system_prompt: 'You are a helpful college AI assistant. Ground your answers in the student\'s study notes.'
      },
      uploadState: {
        status: 'idle', // idle, uploading, analyzing, success
        fileName: '',
        progress: 0
      },
      flashcardState: {
        currentIndex: 0,
        masteredCount: 0,
        isGenerating: false,
        isComplete: false
      },
      quizState: {
        currentIndex: 0,
        selectedOptionIndex: null,
        score: 0,
        isGenerating: false,
        isComplete: false
      }
    };
  }

  init() {
    // Nav links binding
    document.querySelectorAll('[data-route]').forEach(link => {
      link.addEventListener('click', (e) => {
        const route = link.getAttribute('data-route');
        this.navigateTo(route);
      });
    });

    // Load user settings from backend
    this.loadSettings();

    // Fetch documents list from backend
    this.loadDocuments();

    // Handle initial document widget update
    this.updateActiveDocumentWidget();
    
    // Render user profile widget
    this.updateUserProfileWidget();
    
    // Render current active view
    this.renderActiveView();

    this.showToast("Welcome! Interactive study workspace active.", "info");
  }

  async loadSettings() {
    try {
      console.log("[DEBUG] Fetching Settings: GET /api/settings");
      const response = await fetch('/api/settings');
      const result = await response.json();
      if (result.success && result.data) {
        console.log("[DEBUG] Settings received:", result.data);
        this.state.settings = result.data;
        this.updateUserProfileWidget();
      }
    } catch (err) {
      console.warn("Failed to load settings from backend:", err);
      this.state.serverDown = true;
      this.renderActiveView();
    }
  }

  async loadDocuments() {
    try {
      this.state.serverDown = false;
      console.log("[DEBUG] Fetching Documents: GET /api/documents");
      const response = await fetch('/api/documents');
      const result = await response.json();
      if (result.success && result.data) {
        console.log("[DEBUG] Documents list received:", result.data);
        this.state.documents = result.data.map(doc => this.mapBackendDoc(doc));
        
        // Fetch active document ID
        await this.loadActiveDocument();
        
        // Preload active document text details
        await this.ensureActiveDocumentLoaded();
        
        // Re-render UI views
        this.updateActiveDocumentWidget();
        this.renderActiveView();
      } else {
        throw new Error(result.error || "Failed to retrieve documents list.");
      }
    } catch (err) {
      console.error("Failed to load documents from backend:", err);
      this.state.serverDown = true;
      this.renderActiveView();
      this.showToast("Connection to backend service unavailable.", "error");
    }
  }

  async loadActiveDocument() {
    try {
      console.log("[DEBUG] Fetching Active Doc: GET /api/documents/active");
      const response = await fetch('/api/documents/active');
      const result = await response.json();
      if (result.success && result.data) {
        this.state.activeDocumentId = result.data.active_document_id;
        console.log("[DEBUG] Active document ID is:", this.state.activeDocumentId);
      }
    } catch (err) {
      console.error("Failed to load active document ID from backend:", err);
    }
  }

  mapBackendDoc(doc) {
    const bytes = doc.size_bytes;
    let formattedSize = "0 Bytes";
    if (bytes > 0) {
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    return {
      id: doc.id,
      name: doc.name,
      type: doc.type,
      size: formattedSize,
      pageCount: doc.page_count || 1,
      subject: doc.type.toUpperCase() + " notes",
      summary: doc.preview_snippet || "No summary preview available.",
      chatHistory: [
        {
          sender: "assistant",
          text: `Hello! I have indexed **${doc.name}** (containing ${doc.page_count || 1} pages). Ask me any doubts or test yourself with flashcards or quizzes.`,
          time: "02:00 PM"
        }
      ],
      flashcards: [],
      quiz: []
    };
  }

  /**
   * Route Navigations
   */
  async navigateTo(viewName) {
    this.state.currentView = viewName;
    
    // Update active nav button styling
    document.querySelectorAll('[data-route]').forEach(link => {
      const route = link.getAttribute('data-route');
      if (route === viewName) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Update Header Text based on view
    const headerTitle = document.querySelector('#header-title');
    if (headerTitle) {
      const titles = {
        dashboard: 'Study Workspace Dashboard',
        upload: 'Document Processing Center',
        chat: 'Ask AI Doubts',
        flashcards: 'Flashcards Revision Deck',
        quiz: 'Study Assessment Quiz'
      };
      headerTitle.textContent = titles[viewName] || 'Smart College AI';
    }

    // Ensure that active document details are loaded from backend if studying
    if (viewName === 'chat' || viewName === 'flashcards' || viewName === 'quiz') {
      await this.ensureActiveDocumentLoaded();
    }

    if (viewName === 'flashcards') {
      const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
      if (doc && (!doc.flashcards || doc.flashcards.length === 0)) {
        this.resetFlashcards();
        return; // resetFlashcards calls renderActiveView itself
      }
    }

    if (viewName === 'quiz') {
      const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
      if (doc && (!doc.quiz || doc.quiz.length === 0)) {
        this.resetQuiz();
        return; // resetQuiz calls renderActiveView itself
      }
    }

    this.renderActiveView();
  }

  async ensureActiveDocumentLoaded() {
    if (!this.state.activeDocumentId) return;
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (doc && (!doc.content || doc.content === "No summary preview available.")) {
      console.log("[DEBUG] Fetching Active Document details: GET /api/documents/" + this.state.activeDocumentId);
      try {
        const response = await fetch(`/api/documents/${this.state.activeDocumentId}`);
        const result = await response.json();
        if (result.success && result.data) {
          doc.content = result.data.extracted_text || "";
        }
      } catch (err) {
        console.error("Error loading active document details:", err);
      }
    }
  }

  /**
   * State Mutators & Render Hooks
   */
  renderActiveView() {
    const viewContainer = document.querySelector('#view-container');
    if (!viewContainer) return;
    
    // Clear viewport contents
    viewContainer.innerHTML = '';
    
    if (this.state.serverDown) {
      const wrapper = document.createElement('div');
      wrapper.className = 'empty-state';
      wrapper.style.marginTop = '120px';
      wrapper.innerHTML = `
        <div class="empty-state-icon" style="color: var(--danger); background-color: var(--danger-glow); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
          <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </div>
        <h3 class="empty-state-title" style="color: var(--text-primary); font-size: 16px; font-weight: 700;">Backend Server Offline</h3>
        <p class="empty-state-desc" style="max-width: 420px; margin: 8px auto 20px; line-height: 1.5; color: var(--text-secondary); font-size: 13px;">
          Could not establish connection with the FastAPI backend service on port 8000. Please start the server using your terminal:<br>
          <code style="display: block; background: var(--bg-surface); padding: 8px; border-radius: 6px; border: 1px solid var(--border-color); color: var(--accent-primary); margin-top: 10px; font-family: monospace;">py -3.13 -m backend.main</code>
        </p>
        <button class="btn btn-primary" id="retry-server-btn">Retry Connection</button>
      `;
      wrapper.querySelector('#retry-server-btn').addEventListener('click', () => {
        this.state.serverDown = false;
        this.loadSettings();
        this.loadDocuments();
      });
      viewContainer.appendChild(wrapper);
      return;
    }

    let renderedElement;
    switch (this.state.currentView) {
      case 'dashboard':
        renderedElement = Components.renderDashboard(this.state, this);
        break;
      case 'upload':
        renderedElement = Components.renderUpload(this.state, this);
        break;
      case 'chat':
        renderedElement = Components.renderChat(this.state, this);
        break;
      case 'flashcards':
        renderedElement = Components.renderFlashcards(this.state, this);
        break;
      case 'quiz':
        renderedElement = Components.renderQuiz(this.state, this);
        break;
      default:
        renderedElement = document.createElement('div');
        renderedElement.textContent = 'View not found';
    }
    
    viewContainer.appendChild(renderedElement);
  }

  /**
   * Active Document Manager
   */
  async setActiveDocument(docId) {
    console.log("[DEBUG] Activating document context: POST /api/documents/active - ID: " + docId);
    try {
      const response = await fetch('/api/documents/active', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: docId })
      });
      const result = await response.json();
      if (result.success && result.data) {
        this.state.activeDocumentId = result.data.active_document_id;
        
        // Load its full text content
        await this.ensureActiveDocumentLoaded();

        this.updateActiveDocumentWidget();
        this.resetFlashcardsState();
        this.resetQuizState();

        const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
        if (this.state.currentView === 'flashcards' && doc && (!doc.flashcards || doc.flashcards.length === 0)) {
          this.resetFlashcards();
        } else if (this.state.currentView === 'quiz' && doc && (!doc.quiz || doc.quiz.length === 0)) {
          this.resetQuiz();
        } else {
          this.renderActiveView();
        }
      } else {
        this.showToast(result.error || "Failed to set active workspace.", "error");
      }
    } catch (err) {
      console.error("Network error setting active document:", err);
      this.showToast("Network error setting active workspace.", "error");
    }
  }

  updateActiveDocumentWidget() {
    const widget = document.querySelector('#active-doc-widget-container');
    const headerIndicator = document.querySelector('#header-active-doc-indicator');
    if (!widget) return;

    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    
    if (doc) {
      // Sidebar Widget Update
      widget.innerHTML = `
        <div class="active-doc-widget">
          <span class="active-doc-title">Active Workspace</span>
          <div class="active-doc-info">
            <div class="active-doc-icon">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            </div>
            <div>
              <div class="active-doc-name" title="${doc.name}">${doc.name}</div>
              <div class="active-doc-subject">${doc.subject}</div>
            </div>
          </div>
          <div class="active-doc-change" id="widget-change-doc">Switch Document</div>
        </div>
      `;
      widget.querySelector('#widget-change-doc').addEventListener('click', () => {
        this.navigateTo('dashboard');
      });

      // Top Header Indicator Update
      if (headerIndicator) {
        headerIndicator.innerHTML = `
          <div class="active-file-indicator">
            <span class="dot"></span>
            <span>Workspace: <b>${doc.name}</b></span>
          </div>
        `;
      }
    } else {
      widget.innerHTML = `
        <div class="active-doc-widget" style="padding: 12px;">
          <div class="no-doc-card">
            No active notes
          </div>
        </div>
      `;
      if (headerIndicator) {
        headerIndicator.innerHTML = `
          <div class="active-file-indicator">
            <span class="dot offline"></span>
            <span>Workspace Offline</span>
          </div>
        `;
      }
    }
  }

  updateUserProfileWidget() {
    const container = document.querySelector('#user-profile-container');
    if (!container) return;

    const userName = (this.state.settings && this.state.settings.user_name) ? this.state.settings.user_name : "User";
    const userAbout = (this.state.settings && this.state.settings.user_about) ? this.state.settings.user_about : "Active Student";
    const avatarChar = userName.trim() ? userName.trim().charAt(0).toUpperCase() : "U";

    container.innerHTML = `
      <div class="user-profile-widget" id="user-profile-trigger">
        <div class="profile-info">
          <div class="profile-avatar">${avatarChar}</div>
          <div class="profile-details">
            <span class="profile-name" title="${userName}">${userName}</span>
            <span class="profile-role" title="${userAbout}">${userAbout}</span>
          </div>
        </div>
        <div class="profile-actions-trigger" style="transition: transform 0.2s ease;">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
        
        <!-- Profile dropdown menu -->
        <div class="profile-dropdown-menu" id="profile-dropdown">
          <div class="dropdown-item" id="prof-settings-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            <span>Account Settings</span>
          </div>
          <div class="dropdown-item" id="prof-details-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <span>User Profile</span>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item logout" id="prof-logout-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            <span>Log Out</span>
          </div>
        </div>
      </div>
    `;

    // Dropdown toggling logic
    const trigger = container.querySelector('#user-profile-trigger');
    const dropdown = container.querySelector('#profile-dropdown');

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
      
      const arrow = trigger.querySelector('.profile-actions-trigger svg');
      if (arrow) {
        if (dropdown.classList.contains('show')) {
          arrow.style.transform = 'rotate(180deg)';
        } else {
          arrow.style.transform = 'none';
        }
      }
    });

    document.addEventListener('click', () => {
      if (dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
        const arrow = trigger.querySelector('.profile-actions-trigger svg');
        if (arrow) arrow.style.transform = 'none';
      }
    });

    container.querySelector('#prof-settings-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.remove('show');
      const arrow = trigger.querySelector('.profile-actions-trigger svg');
      if (arrow) arrow.style.transform = 'none';
      this.openSettingsModal();
    });

    container.querySelector('#prof-details-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.remove('show');
      const arrow = trigger.querySelector('.profile-actions-trigger svg');
      if (arrow) arrow.style.transform = 'none';
      this.showToast(`Logged in as ${userName} (${userAbout})`, "info");
    });

    container.querySelector('#prof-logout-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.remove('show');
      const arrow = trigger.querySelector('.profile-actions-trigger svg');
      if (arrow) arrow.style.transform = 'none';
      this.showToast("Authentication logout simulated.", "warning");
    });
  }

  openSettingsModal() {
    if (document.querySelector('#settings-modal')) return;

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'settings-modal';
    
    const settings = this.state.settings || {
      user_name: 'User',
      user_about: 'Active Student',
      model: 'local-heuristic',
      ollama_url: 'http://localhost:11434',
      system_prompt: 'You are a helpful college AI assistant. Ground your answers in the student\'s study notes.'
    };

    modal.innerHTML = `
      <div class="modal-card" style="max-width: 500px; width: 90%;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid var(--border-color); padding-bottom:8px;">
          <h3 style="font-size:16px; font-weight:700;">Account & AI Settings</h3>
          <button id="close-settings-modal" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; display:flex; align-items:center; justify-content:center;">
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        
        <form id="settings-form" style="display:flex; flex-direction:column; gap:12px;">
          <div class="form-group" style="display:flex; flex-direction:column; gap:4px;">
            <label style="font-size:12px; color:var(--text-secondary); font-weight:600;">Display Name</label>
            <input type="text" id="settings-username" value="${settings.user_name}" placeholder="User" style="padding:8px 12px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:6px; color:var(--text-primary); font-size:13.5px;" required>
          </div>
          
          <div class="form-group" style="display:flex; flex-direction:column; gap:4px;">
            <label style="font-size:12px; color:var(--text-secondary); font-weight:600;">Bio / Major</label>
            <input type="text" id="settings-about" value="${settings.user_about}" placeholder="Active Student" style="padding:8px 12px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:6px; color:var(--text-primary); font-size:13.5px;">
          </div>
          
          <div class="form-group" style="display:flex; flex-direction:column; gap:4px;">
            <label style="font-size:12px; color:var(--text-secondary); font-weight:600;">Active AI Provider</label>
            <select id="settings-model" style="padding:8px 12px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:6px; color:var(--text-primary); font-size:13.5px;">
              <option value="local" ${(settings.model === 'local' || settings.model === 'local-heuristic') ? 'selected' : ''}>Local Mode (Offline Heuristics)</option>
              <option value="gemini" ${settings.model === 'gemini' ? 'selected' : ''}>Google Gemini API (Cloud)</option>
              <option value="groq" ${settings.model === 'groq' ? 'selected' : ''}>Groq API (Cloud)</option>
            </select>
          </div>
          
          <div class="form-group" style="display:flex; flex-direction:column; gap:4px;">
            <label style="font-size:12px; color:var(--text-secondary); font-weight:600;">Ollama Host URL</label>
            <input type="url" id="settings-ollama-url" value="${settings.ollama_url}" style="padding:8px 12px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:6px; color:var(--text-primary); font-size:13.5px;">
          </div>
          
          <div class="form-group" style="display:flex; flex-direction:column; gap:4px;">
            <label style="font-size:12px; color:var(--text-secondary); font-weight:600;">AI System Prompt</label>
            <textarea id="settings-sys-prompt" style="padding:8px 12px; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:6px; color:var(--text-primary); font-size:13.5px; height:80px; resize:vertical;">${settings.system_prompt}</textarea>
          </div>
          
          <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
            <button type="button" class="btn btn-secondary" id="cancel-settings">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Settings</button>
          </div>
        </form>
      </div>
    `;
    
    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('#close-settings-modal');
    const cancelBtn = modal.querySelector('#cancel-settings');
    const form = modal.querySelector('#settings-form');

    const closeModal = () => {
      if (document.body.contains(modal)) {
        document.body.removeChild(modal);
      }
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const updated = {
        user_name: modal.querySelector('#settings-username').value.trim() || "User",
        user_about: modal.querySelector('#settings-about').value.trim() || "Active Student",
        model: modal.querySelector('#settings-model').value,
        ollama_url: modal.querySelector('#settings-ollama-url').value.trim(),
        system_prompt: modal.querySelector('#settings-sys-prompt').value.trim()
      };

      try {
        const response = await fetch('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updated)
        });
        
        const result = await response.json();
        if (result.success && result.data) {
          this.state.settings = result.data;
          this.updateUserProfileWidget();
          this.showToast("Personalization settings saved!", "success");
          closeModal();
        } else {
          this.showToast("Failed to save settings: " + (result.error || "Unknown error"), "error");
        }
      } catch (err) {
        this.showToast("Network error saving settings.", "error");
        console.error(err);
      }
    });
  }

  confirmDeleteDocument(docId) {
    const doc = this.state.documents.find(d => d.id === docId);
    if (!doc) return;

    // Create modal overlay dynamically
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'delete-confirm-modal';
    overlay.innerHTML = `
      <div class="modal-card">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
          <div style="width:40px; height:40px; border-radius:50%; background-color:var(--danger-glow); color:var(--danger); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          </div>
          <h3 style="font-size:16px; font-weight:700;">Delete Document?</h3>
        </div>
        <p style="font-size:13px; color:var(--text-secondary); line-height:1.5; margin-bottom:6px;">
          Are you sure you want to remove <b>${doc.name}</b> from your workspace?
        </p>
        <p style="font-size:12px; color:var(--text-muted); line-height:1.4;">
          This action will permanently delete all generated study flashcards, active chat threads, and practice test progress associated with this document.
        </p>
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:12px;">
          <button class="btn btn-secondary btn-sm" id="modal-cancel-btn">Cancel</button>
          <button class="btn btn-danger btn-sm" id="modal-delete-btn">Delete Workspace</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    overlay.querySelector('#modal-cancel-btn').addEventListener('click', () => {
      overlay.remove();
    });

    overlay.querySelector('#modal-delete-btn').addEventListener('click', () => {
      this.deleteDocument(docId);
      overlay.remove();
    });

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });
  }

  async deleteDocument(docId) {
    const docIndex = this.state.documents.findIndex(d => d.id === docId);
    if (docIndex === -1) return;

    const docName = this.state.documents[docIndex].name;
    console.log("[DEBUG] Deleting Document: DELETE /api/documents/" + docId);

    try {
      const response = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE'
      });
      const result = await response.json();

      if (result.success) {
        console.log("[DEBUG] Document deleted from backend successfully");
        this.state.documents.splice(docIndex, 1);
        this.showToast(`Document "${docName}" removed from workspace.`, "warning");

        // Sync active document ID from backend re-selection
        await this.loadActiveDocument();
        this.updateActiveDocumentWidget();
        this.renderActiveView();
      } else {
        this.showToast(result.error || "Failed to delete document.", "error");
      }
    } catch (err) {
      console.error("[DEBUG] Document deletion network error:", err);
      this.showToast("Network error deleting document.", "error");
    }
  }

  /**
   * Upload Simulation
   */
  async handleFileUpload(file) {
    if (!file) return;

    if (file.size > 25 * 1024 * 1024) {
      this.showToast("File exceeds 25MB limit", "error");
      return;
    }

    console.log("[DEBUG] Uploading Document: POST /api/documents/upload for " + file.name);
    this.state.uploadState = {
      status: 'uploading',
      fileName: file.name,
      progress: 25
    };
    
    // Switch to upload screen to show progress
    this.navigateTo('upload');

    try {
      const formData = new FormData();
      formData.append('file', file);

      this.state.uploadState.progress = 60;
      this.renderActiveView();

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      });

      this.state.uploadState.progress = 90;
      this.renderActiveView();

      const result = await response.json();

      if (result.success && result.data) {
        console.log("[DEBUG] Upload successful:", result.data);
        const mapped = this.mapBackendDoc(result.data);
        
        // Add to local list
        this.state.documents.push(mapped);
        
        // Explicitly set active document context on backend
        await this.setActiveDocument(mapped.id);
        
        this.state.uploadState.status = 'success';
        this.showToast("Analysis complete! Study workspace generated.", "success");
        this.renderActiveView();
      } else {
        console.error("[DEBUG] Upload failure response:", result.error);
        this.showToast(result.error || "Document upload failed.", "error");
        this.resetUploadState();
      }
    } catch (err) {
      console.error("[DEBUG] Network upload exception:", err);
      this.showToast("Network error uploading document.", "error");
      this.resetUploadState();
    }
  }

  resetUploadState() {
    this.state.uploadState = {
      status: 'idle',
      fileName: '',
      progress: 0
    };
    this.renderActiveView();
  }

  /**
   * Chat Workspace Functions
   */
  async sendChatMessage(text) {
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (!doc) {
      this.showToast("No active document context selected.", "error");
      return;
    }

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add user message to local history
    doc.chatHistory.push({
      sender: "user",
      text: text,
      time: timeStr
    });

    this.renderActiveView(); // Renders user bubble instantly
    this.showTypingIndicator();

    try {
      console.log("[DEBUG] Querying Q&A: POST /api/ai/chat for doc: " + doc.id);
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          document_id: doc.id,
          message: text
        })
      });

      const result = await response.json();
      this.removeTypingIndicator();

      if (result.success && result.data) {
        console.log("[DEBUG] Chat response received:", result.data);
        const reply = result.data;
        
        if (!reply.text || !reply.text.trim()) {
          throw new Error("AI service returned a blank answer context.");
        }
        
        let replyText = reply.text;
        if (reply.citation) {
          replyText += `\n\n*(Source: ${reply.citation})*`;
          if (reply.source_page) {
            replyText += ` [Page ${reply.source_page}]`;
          }
        }

        doc.chatHistory.push({
          sender: "assistant",
          text: replyText,
          time: reply.time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          citation: reply.citation,
          source_excerpt: reply.source_excerpt,
          source_page: reply.source_page
        });
      } else {
        console.error("[DEBUG] Chat endpoint error response:", result.error);
        doc.chatHistory.push({
          sender: "assistant",
          text: `⚠️ **Error:** ${result.error || "Failed to query the AI study assistant."}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
        this.showToast(result.error || "AI query failed.", "error");
      }
    } catch (err) {
      console.error("[DEBUG] Chat connection exception:", err);
      this.removeTypingIndicator();
      doc.chatHistory.push({
        sender: "assistant",
        text: "⚠️ **Connection Error:** Could not contact the study assistant service.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
      this.showToast("Network error querying assistant.", "error");
    }

    this.renderActiveView();
  }

  showTypingIndicator() {
    const list = document.querySelector('#chat-msg-list');
    if (!list) return;

    const loader = document.createElement('div');
    loader.className = 'message-bubble assistant typing-indicator-bubble';
    loader.id = 'chat-typing-indicator';
    loader.innerHTML = `
      <div class="message-avatar">AI</div>
      <div>
        <div class="message-content" style="display:flex; align-items:center; gap:4px; padding: 12px 16px;">
          <span class="upload-spinner" style="width:14px; height:14px; border-width:1.5px;"></span>
          <span style="color:var(--text-muted); font-size:12px;">AI is researching notes...</span>
        </div>
      </div>
    `;
    list.appendChild(loader);
    list.scrollTop = list.scrollHeight;
  }

  removeTypingIndicator() {
    const indicator = document.querySelector('#chat-typing-indicator');
    if (indicator) indicator.remove();
  }

  /**
   * Flashcard Deck Navigation
   */
  nextFlashcard(wasMastered) {
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (!doc) return;

    if (wasMastered) {
      this.state.flashcardState.masteredCount++;
    }

    if (this.state.flashcardState.currentIndex + 1 < doc.flashcards.length) {
      this.state.flashcardState.currentIndex++;
      this.renderActiveView();
    } else {
      this.state.flashcardState.isComplete = true;
      this.renderActiveView();
    }
  }

  prevFlashcard() {
    if (this.state.flashcardState.currentIndex > 0) {
      this.state.flashcardState.currentIndex--;
      this.renderActiveView();
    }
  }

  async resetFlashcards() {
    this.resetFlashcardsState();
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (!doc) return;

    if (!doc.flashcards || doc.flashcards.length === 0) {
      console.log("[DEBUG] Compiling Flashcards: POST /api/ai/flashcards for " + doc.id);
      this.state.flashcardState.isGenerating = true;
      this.renderActiveView();

      try {
        const response = await fetch('/api/ai/flashcards', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            document_id: doc.id,
            count: 5
          })
        });
        const result = await response.json();
        this.state.flashcardState.isGenerating = false;

        if (result.success && result.data) {
          if (!Array.isArray(result.data) || result.data.length === 0) {
            throw new Error(result.error || "AI service returned empty flashcard list.");
          }
          console.log("[DEBUG] Flashcards generated:", result.data);
          doc.flashcards = result.data;
        } else {
          this.showToast(result.error || "Failed to compile flashcards.", "error");
        }
      } catch (err) {
        console.error("[DEBUG] Flashcards API exception:", err);
        this.state.flashcardState.isGenerating = false;
        this.showToast("Network error generating flashcards.", "error");
      }
    }

    this.renderActiveView();
  }

  resetFlashcardsState() {
    this.state.flashcardState = {
      currentIndex: 0,
      masteredCount: 0,
      isGenerating: false,
      isComplete: false
    };
  }

  /**
   * Quiz Actions
   */
  answerQuizQuestion(optionIndex) {
    this.state.quizState.selectedOptionIndex = optionIndex;
    
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    const currentQ = doc.quiz[this.state.quizState.currentIndex];
    
    if (optionIndex === currentQ.correctIndex) {
      this.state.quizState.score++;
      this.showToast("Correct! Great job.", "success");
    } else {
      this.showToast("Incorrect answer. Read the AI explanation.", "error");
    }

    this.renderActiveView();
  }

  nextQuizQuestion() {
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (!doc) return;

    if (this.state.quizState.currentIndex + 1 < doc.quiz.length) {
      this.state.quizState.currentIndex++;
      this.state.quizState.selectedOptionIndex = null;
      this.renderActiveView();
    } else {
      this.state.quizState.isComplete = true;
      this.renderActiveView();
    }
  }

  async resetQuiz() {
    this.resetQuizState();
    const doc = this.state.documents.find(d => d.id === this.state.activeDocumentId);
    if (!doc) return;

    if (!doc.quiz || doc.quiz.length === 0) {
      console.log("[DEBUG] Compiling Quiz: POST /api/ai/quiz for " + doc.id);
      this.state.quizState.isGenerating = true;
      this.renderActiveView();

      try {
        const response = await fetch('/api/ai/quiz', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            document_id: doc.id,
            count: 5
          })
        });
        const result = await response.json();
        this.state.quizState.isGenerating = false;

        if (result.success && result.data) {
          if (!Array.isArray(result.data) || result.data.length === 0) {
            throw new Error(result.error || "AI service returned empty quiz list.");
          }
          console.log("[DEBUG] Quiz generated:", result.data);
          doc.quiz = result.data;
        } else {
          this.showToast(result.error || "Failed to generate quiz.", "error");
        }
      } catch (err) {
        console.error("[DEBUG] Quiz API exception:", err);
        this.state.quizState.isGenerating = false;
        this.showToast("Network error generating quiz.", "error");
      }
    }

    this.renderActiveView();
  }

  resetQuizState() {
    this.state.quizState = {
      currentIndex: 0,
      selectedOptionIndex: null,
      score: 0,
      isGenerating: false,
      isComplete: false
    };
  }

  /**
   * Toast Notification Controller
   */
  showToast(message, type = 'info') {
    const container = document.querySelector('#toast-holder');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div style="font-weight: 500;">${message}</div>
      <div class="toast-close">${Icons.x}</div>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => {
      toast.remove();
    });

    container.appendChild(toast);

    // Auto dismiss after 3 seconds
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.5s ease';
      setTimeout(() => toast.remove(), 500);
    }, 3000);
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.AppInstance = new SmartCollegeApp();
  window.AppInstance.init();
});
