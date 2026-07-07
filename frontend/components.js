/**
 * UI Components for Smart College AI Assistant.
 * Bundles helper icons and modular render methods for each workspace screen.
 */

// SVG Icons helper object
const Icons = {
  dashboard: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>`,
  upload: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>`,
  chat: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
  flashcard: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>`,
  quiz: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>`,
  document: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
  plus: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
  send: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
  arrowRight: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`,
  check: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  x: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
  info: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
  brain: `<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3 3 0 0 1 0-4.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3 3 0 0 0 0-4.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2z"></path></svg>`
};

const Components = {
  /**
   * Screen 1: Dashboard View
   */
  renderDashboard: function(state, app) {
    const totalDocs = state.documents.length;
    const totalQueries = state.documents.reduce((acc, doc) => acc + (doc.chatHistory ? doc.chatHistory.length - 1 : 0), 0);
    const totalFlashcards = state.documents.reduce((acc, doc) => acc + (doc.flashcards ? doc.flashcards.length : 0), 0);
    
    // Quick statistics calculation
    const html = `
      <div class="welcome-section">
        <h1 class="welcome-title">Smart College AI Assistant</h1>
        <p class="welcome-desc">Upload your lecture notes, chemistry slides, or study PDFs, and instantly transform them into a comprehensive interactive learning workspace.</p>
      </div>

      <div class="stats-grid">
        <div class="card stat-card">
          <div class="stat-icon">${Icons.document}</div>
          <div class="stat-info">
            <span class="stat-value">${totalDocs}</span>
            <span class="stat-label">Study Materials</span>
          </div>
        </div>
        <div class="card stat-card">
          <div class="stat-icon">${Icons.chat}</div>
          <div class="stat-info">
            <span class="stat-value">${totalQueries}</span>
            <span class="stat-label">Doubts Solved</span>
          </div>
        </div>
        <div class="card stat-card">
          <div class="stat-icon">${Icons.brain}</div>
          <div class="stat-info">
            <span class="stat-value">${totalFlashcards}</span>
            <span class="stat-label">Revision Flashcards</span>
          </div>
        </div>
        <div class="card stat-card">
          <div class="stat-icon">${Icons.quiz}</div>
          <div class="stat-info">
            <span class="stat-value">85%</span>
            <span class="stat-label">Average Quiz Score</span>
          </div>
        </div>
      </div>

      <div class="dashboard-layout">
        <!-- Left: Upload workspace entry -->
        <div class="card" style="display: flex; flex-direction: column; gap: 20px;">
          <h3 style="font-size: 16px; font-weight: 600;">Create Study Workspace</h3>
          <p class="card-desc">Drag and drop any lecture slides, notes, or research papers (PDF, TXT) here. Our AI will analyze, index, and organize key information instantly.</p>
          
          <div class="dropzone" id="dash-dropzone">
            <div class="dropzone-icon">${Icons.upload}</div>
            <div class="dropzone-title">Upload lecture notes or PDF</div>
            <div class="dropzone-subtitle">Drag & drop files here, or <span style="color: var(--accent-primary); font-weight: 600;">browse files</span></div>
            <div class="dropzone-restrictions">Supports PDF, TXT (Max 25MB)</div>
            <input type="file" id="dash-file-input" class="file-input" accept=".pdf,.txt">
          </div>
        </div>

        <!-- Right: Recent/Active Documents -->
        <div>
          <div class="dashboard-panel-title">
            <span>Indexed Documents</span>
            <span>${totalDocs} Files</span>
          </div>
          <div class="recent-docs-list">
            ${state.documents.length === 0 
              ? `
                <div class="no-doc-card" style="padding: 32px; font-size: 13px; border-style: dashed; text-align: center; color: var(--text-muted);">
                  No indexed study materials. Please upload a PDF or notes file to get started.
                </div>
              `
              : state.documents.map(doc => {
                  const isActive = state.activeDocumentId === doc.id;
                  return `
                    <div class="doc-list-item" style="${isActive ? 'border-color: var(--accent-primary); box-shadow: 0 0 10px rgba(99, 102, 241, 0.05);' : ''}">
                      <div class="doc-item-left">
                        <div class="doc-item-icon" style="${isActive ? 'background-color: rgba(99,102,241,0.2); color: #fff;' : ''}">
                          ${Icons.document}
                        </div>
                        <div class="doc-item-meta">
                          <span class="doc-item-name" title="${doc.name}">${doc.name}</span>
                          <div class="doc-item-details">
                            <span>${doc.size}</span>
                            <span>•</span>
                            <span>${doc.pageCount} pages</span>
                            <span>•</span>
                            <span class="doc-item-badge">${doc.subject}</span>
                          </div>
                        </div>
                      </div>
                      <div class="doc-item-actions" style="display: flex; align-items: center; gap: 8px;">
                        ${isActive 
                          ? `<span class="active-file-indicator" style="background: transparent; border: none; padding: 0; margin-right: 6px;"><span class="dot"></span></span>`
                          : `<button class="btn btn-secondary btn-sm select-doc-btn" data-id="${doc.id}">Activate</button>`
                        }
                        <button class="btn btn-primary btn-sm chat-doc-btn" data-id="${doc.id}">Study</button>
                        <button class="btn btn-icon btn-sm delete-doc-btn" data-id="${doc.id}" title="Remove Document" style="color: var(--text-muted); background: transparent; border: none; padding: 4px; display: inline-flex; align-items: center; justify-content: center; height: 30px; width: 30px; cursor: pointer;">
                          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                        </button>
                      </div>
                    </div>
                  `;
                }).join('')}
          </div>
        </div>
      </div>
    `;

    // Return HTML and attach event listeners
    const element = document.createElement('div');
    element.innerHTML = html;

    // Attach File Upload triggers
    const dropzone = element.querySelector('#dash-dropzone');
    const fileInput = element.querySelector('#dash-file-input');
    
    dropzone.addEventListener('click', () => fileInput.click());
    
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        app.handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        app.handleFileUpload(e.target.files[0]);
      }
    });

    // Attach Activate Document events
    element.querySelectorAll('.select-doc-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        app.setActiveDocument(id);
        app.showToast("Document activated! You can now chat or practice.", "success");
      });
    });

    // Attach Study Workspace events
    element.querySelectorAll('.chat-doc-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.getAttribute('data-id');
        app.setActiveDocument(id);
        app.navigateTo('chat');
      });
    });

    // Attach Delete Document events
    element.querySelectorAll('.delete-doc-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = btn.getAttribute('data-id');
        app.confirmDeleteDocument(id);
      });
    });

    return element;
  },

  /**
   * Screen 2: Upload Workspace View
   */
  renderUpload: function(state, app) {
    const container = document.createElement('div');
    container.className = 'upload-workspace-container';

    // Header
    const titleSection = document.createElement('div');
    titleSection.style.textAlign = 'center';
    titleSection.style.marginBottom = '12px';
    titleSection.innerHTML = `
      <h1 style="font-size: 26px; font-weight: 700; margin-bottom: 8px;">Upload Notes & Materials</h1>
      <p style="font-size: 14px; color: var(--text-secondary); max-width: 500px; margin: 0 auto;">Connect new notes to your AI study workspace. The AI will extract content and auto-generate flashcards and self-tests.</p>
    `;
    container.appendChild(titleSection);

    // If uploading state
    if (state.uploadState.status === 'uploading' || state.uploadState.status === 'analyzing') {
      const isAnalyzing = state.uploadState.status === 'analyzing';
      const statusCard = document.createElement('div');
      statusCard.className = 'upload-status-card';
      statusCard.innerHTML = `
        <div class="upload-status-info">
          <div class="upload-status-details">
            <div class="upload-spinner"></div>
            <div>
              <h4 style="font-size: 14px; font-weight: 600;">${isAnalyzing ? 'AI Analyzing Document...' : 'Uploading File...'}</h4>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;" id="upload-status-text">
                ${isAnalyzing ? 'Extracting text and generating study components...' : `Uploading ${state.uploadState.fileName} (${state.uploadState.progress}%)`}
              </p>
            </div>
          </div>
          <span style="font-size: 13px; font-weight: 600; color: var(--accent-primary);" id="upload-percentage">
            ${isAnalyzing ? 'Please wait' : `${state.uploadState.progress}%`}
          </span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar" style="width: ${isAnalyzing ? '85%' : `${state.uploadState.progress}%`}"></div>
        </div>
      `;
      container.appendChild(statusCard);
      
      // Simulating a sequence of analysis updates if in analyzing state
      if (isAnalyzing) {
        const statuses = [
          "Parsing document formatting...",
          "Indexing text for vector search...",
          "Generating contextual summaries...",
          "Compiling key conceptual flashcards...",
          "Writing practice quiz options..."
        ];
        let index = 0;
        const interval = setInterval(() => {
          const textEl = statusCard.querySelector('#upload-status-text');
          if (textEl && index < statuses.length) {
            textEl.textContent = statuses[index++];
          } else {
            clearInterval(interval);
          }
        }, 1200);
      }
      return container;
    }

    // Success State
    if (state.uploadState.status === 'success') {
      const activeDoc = state.documents.find(d => d.id === state.activeDocumentId);
      const successCard = document.createElement('div');
      successCard.className = 'card';
      successCard.style.textAlign = 'center';
      successCard.style.padding = '40px';
      successCard.style.display = 'flex';
      successCard.style.flexDirection = 'column';
      successCard.style.alignItems = 'center';
      successCard.style.gap = '20px';
      
      successCard.innerHTML = `
        <div style="width: 56px; height: 56px; border-radius: 50%; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); display: flex; align-items: center; justify-content: center; color: var(--success);">
          ${Icons.check}
        </div>
        <div>
          <h3 style="font-size: 18px; font-weight: 700;">Workspace Ready!</h3>
          <p class="card-desc" style="margin-top: 6px;">Successfully indexed <b>${state.uploadState.fileName}</b>. AI model has fully processed the notes.</p>
        </div>
        
        <!-- Summary Preview Box -->
        <div style="background-color: var(--bg-surface-elevated); border: 1px solid var(--border-color); padding: 18px; border-radius: var(--border-radius); width: 100%; text-align: left; margin: 8px 0;">
          <h4 style="font-size: 13px; font-weight: 600; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
            ${Icons.info} AI Summary Note
          </h4>
          <p style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.6;">${activeDoc ? activeDoc.summary : ''}</p>
        </div>

        <div style="display: flex; gap: 12px; margin-top: 10px;">
          <button class="btn btn-secondary" id="btn-upload-another">Upload Another</button>
          <button class="btn btn-primary" id="btn-start-studying">Start Studying</button>
        </div>
      `;
      
      successCard.querySelector('#btn-upload-another').addEventListener('click', () => {
        app.resetUploadState();
      });
      successCard.querySelector('#btn-start-studying').addEventListener('click', () => {
        app.navigateTo('chat');
      });

      container.appendChild(successCard);
      return container;
    }

    // Default: Dropzone picker
    const dropzone = document.createElement('div');
    dropzone.className = 'dropzone';
    dropzone.innerHTML = `
      <div class="dropzone-icon">${Icons.upload}</div>
      <div class="dropzone-title">Upload your study material</div>
      <div class="dropzone-subtitle">Drag & drop files here, or <span style="color: var(--accent-primary); font-weight: 600;">browse files</span></div>
      <div class="dropzone-restrictions">Supports PDF, TXT, DOCX (Max 25MB)</div>
      <input type="file" id="workspace-file-input" class="file-input" accept=".pdf,.txt">
    `;

    dropzone.addEventListener('click', () => dropzone.querySelector('#workspace-file-input').click());
    
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        app.handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    dropzone.querySelector('#workspace-file-input').addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        app.handleFileUpload(e.target.files[0]);
      }
    });

    container.appendChild(dropzone);
    return container;
  },

  /**
   * Screen 3: Chat with Notes Workspace
   */
  renderChat: function(state, app) {
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-workspace';

    // If no document is active, display empty state
    if (!state.activeDocumentId) {
      wrapper.style.display = 'block';
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="empty-state-icon">${Icons.document}</div>
          <h3 class="empty-state-title">No Active Study Document</h3>
          <p class="empty-state-desc">Select an existing document from the Dashboard, or upload new notes to start asking doubts and querying equations.</p>
          <button class="btn btn-primary" id="empty-chat-btn">Go to Dashboard</button>
        </div>
      `;
      wrapper.querySelector('#empty-chat-btn').addEventListener('click', () => {
        app.navigateTo('dashboard');
      });
      return wrapper;
    }

    const doc = state.documents.find(d => d.id === state.activeDocumentId);
    if (!doc) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="upload-spinner" style="width: 32px; height: 32px; border-width: 3.5px; margin-bottom: 20px; border-color: rgba(99, 102, 241, 0.1); border-top-color: var(--accent-primary);"></div>
          <h3 class="empty-state-title">Loading Active Workspace...</h3>
          <p class="empty-state-desc">Synchronizing study materials from backend storage.</p>
        </div>
      `;
      return wrapper;
    }

    // Left Panel: Document Viewer
    const docViewer = document.createElement('div');
    docViewer.className = 'doc-viewer-panel';
    docViewer.innerHTML = `
      <div class="panel-header">
        <div class="panel-title-text">
          <div style="color: var(--accent-primary);">${Icons.document}</div>
          <span title="${doc.name}">${doc.name}</span>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); font-weight: 500;">
          ${doc.pageCount} Pages • Reference Book
        </div>
      </div>
      <div class="doc-viewer-body" id="doc-viewer-body-content">
        <!-- Render text contents dynamically with sections -->
        ${this.formatDocumentMarkdown(doc.content)}
      </div>
    `;
    wrapper.appendChild(docViewer);

    // Right Panel: Chat Thread
    const chatPanel = document.createElement('div');
    chatPanel.className = 'chat-interface-panel';
    
    // Messages list
    const messageList = document.createElement('div');
    messageList.className = 'chat-message-list';
    messageList.id = 'chat-msg-list';
    
    if (doc.chatHistory && doc.chatHistory.length > 0) {
      doc.chatHistory.forEach(msg => {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${msg.sender}`;
        
        const avatar = msg.sender === 'user' ? 'S' : 'AI';
        const avatarClass = msg.sender === 'user' ? 'user-avatar' : '';
        
        // Render text + optional citation badges
        let renderedText = msg.text;
        // Parse simple citations e.g. [Page 1] or [Page 1.3]
        renderedText = renderedText.replace(/\[Page\s+(\d+(?:\.\d+)?)\]/g, (match, pNum) => {
          return `<span class="citation-link" data-page="${pNum}">Ref: Ch ${pNum}</span>`;
        });

        let speakerHtml = '';
        if (msg.sender === 'assistant') {
          const rawText = msg.text.replace(/<[^>]*>/g, '').replace(/\[[^\]]*\]/g, '').replace(/"/g, '&quot;');
          speakerHtml = `
            <button class="chat-speaker-btn" data-text="${rawText}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; padding: 2px; border-radius: 4px; transition: all 0.2s; margin-left: 6px; vertical-align: middle;" title="Speak answer">
              <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
            </button>
          `;
        }

        bubble.innerHTML = `
          <div class="message-avatar ${avatarClass}">${avatar}</div>
          <div>
            <div class="message-content">
              ${this.parseMarkdownParagraphs(renderedText)}
            </div>
            <div style="display: flex; align-items: center; gap: 4px; margin-top: 2px;">
              <span class="message-time">${msg.time}</span>
              ${speakerHtml}
            </div>
          </div>
        `;
        messageList.appendChild(bubble);
      });
    }

    // Suggestions box if history has only welcome message
    const showSuggestions = doc.chatHistory.length <= 1;
    if (showSuggestions && doc.chatSuggestions) {
      const suggestionsBox = document.createElement('div');
      suggestionsBox.className = 'chat-suggestions-container';
      suggestionsBox.innerHTML = `
        <div class="chat-empty-icon">${Icons.brain}</div>
        <h4 class="chat-suggestions-title">Ask doubts about these notes</h4>
        <p class="chat-suggestions-desc">Click on any suggested prompt below or type your own question regarding formulas, concepts, or summaries.</p>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${doc.chatSuggestions.map(sug => `
            <div class="suggestion-pill" data-text="${sug}">
              <span>${sug}</span>
              ${Icons.arrowRight}
            </div>
          `).join('')}
        </div>
      `;
      
      // Hook click events to suggested prompts
      suggestionsBox.querySelectorAll('.suggestion-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
          const promptText = pill.getAttribute('data-text');
          app.sendChatMessage(promptText);
        });
      });
      messageList.appendChild(suggestionsBox);
    }

    chatPanel.appendChild(messageList);

    // Composer Input
    const composer = document.createElement('div');
    composer.className = 'chat-composer';
    composer.innerHTML = `
      <div class="composer-input-container">
        <textarea class="chat-input" placeholder="Ask a doubt about '${doc.name}'..." id="chat-textarea-input" rows="1"></textarea>
        <div class="composer-actions">
          <button class="btn btn-primary btn-icon" id="chat-send-btn" style="border-radius: 50%; width: 36px; height: 36px; padding: 0;">
            ${Icons.send}
          </button>
        </div>
      </div>
    `;

    // Composer action triggers
    const textarea = composer.querySelector('#chat-textarea-input');
    const sendBtn = composer.querySelector('#chat-send-btn');

    const handleSend = () => {
      const text = textarea.value.trim();
      if (text) {
        app.sendChatMessage(text);
        textarea.value = '';
        textarea.style.height = 'auto';
      }
    };

    textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });

    sendBtn.addEventListener('click', handleSend);

    chatPanel.appendChild(composer);
    wrapper.appendChild(chatPanel);

    // Auto-scroll chat list to bottom
    setTimeout(() => {
      messageList.scrollTop = messageList.scrollHeight;
    }, 50);

    // Hook citation and speaker click behaviors
    messageList.addEventListener('click', (e) => {
      const citation = e.target.closest('.citation-link');
      const speaker = e.target.closest('.chat-speaker-btn');
      
      if (speaker) {
        const text = speaker.getAttribute('data-text');
        window.speechSynthesis.cancel();
        if (text) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.95;
          window.speechSynthesis.speak(utterance);
        }
        return;
      }
      
      if (citation) {
        const pageNum = citation.getAttribute('data-page');
        const docBody = wrapper.querySelector('#doc-viewer-body-content');
        
        // Find header matching Section or heading containing pageNum
        const headers = Array.from(docBody.querySelectorAll('h1, h2, h3'));
        const targetHeader = headers.find(h => h.textContent.includes(pageNum) || h.textContent.includes(`1.${pageNum}`));
        
        if (targetHeader) {
          targetHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
          // Flash highlight color
          targetHeader.style.backgroundColor = 'rgba(99, 102, 241, 0.15)';
          targetHeader.style.transition = 'background-color 0.3s ease';
          setTimeout(() => {
            targetHeader.style.backgroundColor = 'transparent';
          }, 1500);
        } else {
          // If no heading matches, scroll to top or top sections
          const sections = Array.from(docBody.querySelectorAll('h2'));
          if (sections.length > 0) {
            sections[0].scrollIntoView({ behavior: 'smooth' });
          }
        }
      }
    });

    return wrapper;
  },

  /**
   * Screen 4: Flashcards Workspace View
   */
  renderFlashcards: function(state, app) {
    const wrapper = document.createElement('div');
    wrapper.style.height = '100%';
    wrapper.style.display = 'flex';
    wrapper.style.flexDirection = 'column';

    // If no document is active
    if (!state.activeDocumentId) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="empty-state-icon">${Icons.brain}</div>
          <h3 class="empty-state-title">No Active Study Document</h3>
          <p class="empty-state-desc">Select or upload a document to generate personalized 3D flashcards for your revision.</p>
          <button class="btn btn-primary" id="empty-fc-btn">Go to Dashboard</button>
        </div>
      `;
      wrapper.querySelector('#empty-fc-btn').addEventListener('click', () => app.navigateTo('dashboard'));
      return wrapper;
    }

    const doc = state.documents.find(d => d.id === state.activeDocumentId);
    if (!doc) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="upload-spinner" style="width: 32px; height: 32px; border-width: 3.5px; margin-bottom: 20px; border-color: rgba(99, 102, 241, 0.1); border-top-color: var(--accent-primary);"></div>
          <h3 class="empty-state-title">Loading Active Workspace...</h3>
          <p class="empty-state-desc">Synchronizing study materials from backend storage.</p>
        </div>
      `;
      return wrapper;
    }

    // If flashcards need generation (loading state simulation)
    if (state.flashcardState.isGenerating) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px; border-style: solid; padding: 50px;">
          <div class="upload-spinner" style="width: 32px; height: 32px; border-width: 3px; margin-bottom: 20px;"></div>
          <h3 class="empty-state-title">Generating Flashcards...</h3>
          <p class="empty-state-desc" style="max-width: 340px;">AI is scanning core concepts, formulas, and definitions from "${doc.name}" to create study cards.</p>
        </div>
      `;
      return wrapper;
    }

    // If deck is complete
    if (state.flashcardState.isComplete) {
      const container = document.createElement('div');
      container.className = 'flashcards-workspace-container';
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 48px 30px; display: flex; flex-direction: column; align-items: center; gap: 20px;">
          <div style="width: 60px; height: 60px; border-radius: 50%; background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); display: flex; align-items: center; justify-content: center; color: var(--accent-primary);">
            ${Icons.brain}
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 700;">Revision Complete!</h3>
            <p class="card-desc" style="margin-top: 6px;">You have successfully gone through all the generated flashcards for this document.</p>
          </div>
          
          <div style="display: flex; gap: 16px; background-color: var(--bg-surface-elevated); padding: 16px 24px; border-radius: var(--border-radius); border: 1px solid var(--border-color); width: 100%; justify-content: space-around; margin: 10px 0;">
            <div style="text-align: center;">
              <span style="font-size: 22px; font-weight: 700; color: var(--success);">${state.flashcardState.masteredCount}</span>
              <p style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-top: 2px;">Mastered</p>
            </div>
            <div style="text-align: center;">
              <span style="font-size: 22px; font-weight: 700; color: var(--warning);">${doc.flashcards.length - state.flashcardState.masteredCount}</span>
              <p style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-top: 2px;">Review Later</p>
            </div>
          </div>

          <div style="display: flex; gap: 12px; margin-top: 10px;">
            <button class="btn btn-secondary" id="btn-fc-restart">Study Again</button>
            <button class="btn btn-primary" id="btn-fc-quiz">Test with Quiz</button>
          </div>
        </div>
      `;

      container.querySelector('#btn-fc-restart').addEventListener('click', () => app.resetFlashcards());
      container.querySelector('#btn-fc-quiz').addEventListener('click', () => app.navigateTo('quiz'));

      wrapper.appendChild(container);
      return wrapper;
    }

    // Active Flashcard Deck View
    const currentIndex = state.flashcardState.currentIndex;
    const cards = doc.flashcards || [];
    const totalCards = cards.length;

    if (totalCards === 0) {
      const container = document.createElement('div');
      container.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="empty-state-icon" style="color: var(--warning);">${Icons.brain}</div>
          <h3 class="empty-state-title">No Flashcards Compiled</h3>
          <p class="empty-state-desc" style="max-width: 320px; margin: 8px auto 20px; line-height: 1.4; color: var(--text-secondary); font-size: 13px;">
            Could not generate flashcards from this notes context. Click below to retry compiling the study deck.
          </p>
          <button class="btn btn-primary" id="btn-fc-retry-generate">Generate Flashcards</button>
        </div>
      `;
      container.querySelector('#btn-fc-retry-generate').addEventListener('click', () => {
        app.resetFlashcards();
      });
      wrapper.appendChild(container);
      return wrapper;
    }

    const currentCard = cards[currentIndex];
    const progressPercent = Math.round((currentIndex / totalCards) * 100);

    const container = document.createElement('div');
    container.className = 'flashcards-workspace-container';
    container.innerHTML = `
      <!-- Progress row -->
      <div class="flashcard-progress-bar-wrapper">
        <span style="font-weight: 500;">Learning: <b style="color: var(--text-primary);">${doc.name}</b></span>
        <span style="font-size: 12px; font-weight: 600;">Card ${currentIndex + 1} of ${totalCards}</span>
      </div>
      
      <div class="progress-bar-container" style="height: 4px; margin-top: -12px;">
        <div class="progress-bar" style="width: ${progressPercent}%"></div>
      </div>

      <!-- 3D Card Scene -->
      <div class="flashcard-scene" id="fc-scene-box">
        <div class="flashcard-card" id="fc-card-body">
          <!-- Front side: Question -->
          <div class="flashcard-face flashcard-front">
            <button class="speaker-btn" data-text="${currentCard.question.replace(/"/g, '&quot;')}" style="position: absolute; top: 12px; right: 12px; background: transparent; border: none; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 4px; border-radius: 4px; transition: all 0.2s;" title="Listen to question">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
            </button>
            <span class="flashcard-badge" style="background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.2); max-width: 80%; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
              ${currentCard.source_reference ? `Grounded: ${currentCard.source_reference}` : 'Concept Question'}
            </span>
            <p class="flashcard-text">${currentCard.question}</p>
            <div class="flashcard-hint">
              <span>Click Card to Flip</span>
              <span>•</span>
              <span style="color: var(--accent-primary);">View Answer</span>
            </div>
          </div>
          <!-- Back side: Answer -->
          <div class="flashcard-face flashcard-back">
            <button class="speaker-btn" data-text="${currentCard.answer.replace(/"/g, '&quot;')}" style="position: absolute; top: 12px; right: 12px; background: transparent; border: none; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 4px; border-radius: 4px; transition: all 0.2s;" title="Listen to answer">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
            </button>
            <span class="flashcard-badge" style="background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.2); max-width: 80%; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
              ${currentCard.source_reference ? `Grounded: ${currentCard.source_reference}` : 'AI Explanation'}
            </span>
            <p class="flashcard-text" style="font-size: 16px; font-weight: 500; text-align: left; line-height: 1.6;">${currentCard.answer}</p>
            <div class="flashcard-hint">
              <span>Click Card to Flip</span>
              <span>•</span>
              <span style="color: var(--accent-primary);">View Question</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="flashcard-controls">
        <button class="btn btn-secondary btn-icon" id="fc-prev-btn" ${currentIndex === 0 ? 'disabled style="opacity:0.3; cursor:not-allowed;"' : ''}>
          <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
        </button>
        
        <div class="fc-rating-buttons">
          <button class="btn btn-secondary btn-danger" style="gap:6px;" id="fc-failed-btn">
            ${Icons.x} Review Again
          </button>
          <button class="btn btn-primary" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2); gap: 6px;" id="fc-passed-btn">
            ${Icons.check} Got it!
          </button>
        </div>

        <button class="btn btn-secondary btn-icon" id="fc-next-btn">
          <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </button>
      </div>
    `;

    // Hook Flip events
    const cardBody = container.querySelector('#fc-card-body');
    const sceneBox = container.querySelector('#fc-scene-box');
    sceneBox.addEventListener('click', (e) => {
      // Don't flip if clicking inside buttons or speaker button
      if (!e.target.closest('.btn') && !e.target.closest('.speaker-btn')) {
        cardBody.classList.toggle('flipped');
      }
    });

    // Hook voice play events
    container.querySelectorAll('.speaker-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = btn.getAttribute('data-text');
        window.speechSynthesis.cancel();
        if (text) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.95;
          window.speechSynthesis.speak(utterance);
        }
      });
    });

    // Nav events
    container.querySelector('#fc-prev-btn').addEventListener('click', () => {
      app.prevFlashcard();
    });
    
    container.querySelector('#fc-next-btn').addEventListener('click', () => {
      app.nextFlashcard(false); // don't count as mastered
    });

    container.querySelector('#fc-failed-btn').addEventListener('click', () => {
      app.nextFlashcard(false);
    });

    container.querySelector('#fc-passed-btn').addEventListener('click', () => {
      app.nextFlashcard(true);
    });

    wrapper.appendChild(container);
    return wrapper;
  },

  /**
   * Screen 5: Quiz Workspace View
   */
  renderQuiz: function(state, app) {
    const wrapper = document.createElement('div');
    wrapper.style.height = '100%';
    wrapper.style.display = 'flex';
    wrapper.style.flexDirection = 'column';

    // If no document is active
    if (!state.activeDocumentId) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="empty-state-icon">${Icons.quiz}</div>
          <h3 class="empty-state-title">No Active Study Document</h3>
          <p class="empty-state-desc">Select or upload notes to generate a self-evaluating practice quiz dynamically from the material.</p>
          <button class="btn btn-primary" id="empty-qz-btn">Go to Dashboard</button>
        </div>
      `;
      wrapper.querySelector('#empty-qz-btn').addEventListener('click', () => app.navigateTo('dashboard'));
      return wrapper;
    }

    const doc = state.documents.find(d => d.id === state.activeDocumentId);
    if (!doc) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="upload-spinner" style="width: 32px; height: 32px; border-width: 3.5px; margin-bottom: 20px; border-color: rgba(99, 102, 241, 0.1); border-top-color: var(--accent-primary);"></div>
          <h3 class="empty-state-title">Loading Active Workspace...</h3>
          <p class="empty-state-desc">Synchronizing study materials from backend storage.</p>
        </div>
      `;
      return wrapper;
    }

    // If quiz is generating (loading state simulation)
    if (state.quizState.isGenerating) {
      wrapper.innerHTML = `
        <div class="empty-state" style="margin-top: 100px; border-style: solid; padding: 50px;">
          <div class="upload-spinner" style="width: 32px; height: 32px; border-width: 3px; margin-bottom: 20px;"></div>
          <h3 class="empty-state-title">Generating Practice Quiz...</h3>
          <p class="empty-state-desc" style="max-width: 340px;">AI is writing multiple-choice questions, distilling options, and compiling answers based on "${doc.name}".</p>
        </div>
      `;
      return wrapper;
    }

    // If quiz is finished
    if (state.quizState.isComplete) {
      const totalQuestions = doc.quiz.length;
      const score = state.quizState.score;
      const pct = Math.round((score / totalQuestions) * 100);
      
      let feedbackTitle = "Keep Practicing!";
      let feedbackText = "Take another look at the document notes and try again. Active testing is the best way to form long-term memories.";
      
      if (pct >= 80) {
        feedbackTitle = "Outstanding Job!";
        feedbackText = "You've fully mastered this study material. Your understanding of scheduling and architecture principles is solid!";
      } else if (pct >= 60) {
        feedbackTitle = "Good Progress!";
        feedbackText = "You have a solid baseline. Reviewing incorrect answers in the summary can help push you to full mastery.";
      }

      const container = document.createElement('div');
      container.className = 'quiz-workspace-container';
      container.innerHTML = `
        <div class="quiz-result-card">
          <div class="quiz-score-circle">
            <span class="quiz-score-number">${score}</span>
            <span class="quiz-score-fraction">of ${totalQuestions} Correct</span>
          </div>
          <h3 class="quiz-feedback-title">${feedbackTitle}</h3>
          <p class="quiz-feedback-text">${feedbackText}</p>
          
          <div style="display: flex; gap: 12px; margin-top: 16px;">
            <button class="btn btn-secondary" id="btn-qz-restart">Retake Quiz</button>
            <button class="btn btn-primary" id="btn-qz-back">Back to Workspace</button>
          </div>
        </div>
      `;

      container.querySelector('#btn-qz-restart').addEventListener('click', () => app.resetQuiz());
      container.querySelector('#btn-qz-back').addEventListener('click', () => app.navigateTo('chat'));

      wrapper.appendChild(container);
      return wrapper;
    }

    // Active Quiz View
    const quiz = doc.quiz || [];
    const totalQ = quiz.length;

    if (totalQ === 0) {
      const container = document.createElement('div');
      container.innerHTML = `
        <div class="empty-state" style="margin-top: 100px;">
          <div class="empty-state-icon" style="color: var(--warning);">${Icons.quiz}</div>
          <h3 class="empty-state-title">No Quiz Questions Compiled</h3>
          <p class="empty-state-desc" style="max-width: 320px; margin: 8px auto 20px; line-height: 1.4; color: var(--text-secondary); font-size: 13px;">
            Could not generate practice questions from this notes context. Click below to retry compiling the quiz.
          </p>
          <button class="btn btn-primary" id="btn-qz-retry-generate">Generate Quiz</button>
        </div>
      `;
      container.querySelector('#btn-qz-retry-generate').addEventListener('click', () => {
        app.resetQuiz();
      });
      wrapper.appendChild(container);
      return wrapper;
    }

    const currentIndex = state.quizState.currentIndex;
    const currentQ = quiz[currentIndex];
    const isAnswered = state.quizState.selectedOptionIndex !== null;

    const container = document.createElement('div');
    container.className = 'quiz-workspace-container';
    container.innerHTML = `
      <div class="quiz-header-row">
        <span style="font-weight: 500;">Active Quiz: <b style="color: var(--text-primary);">${doc.name}</b></span>
        <span style="font-weight: 600;">Question ${currentIndex + 1} of ${totalQ}</span>
      </div>

      <div class="progress-bar-container" style="height: 4px; margin-top: -8px;">
        <div class="progress-bar" style="width: ${Math.round((currentIndex / totalQ) * 100)}%"></div>
      </div>

      <div class="quiz-question-card">
        ${currentQ.source_reference ? `
          <div style="margin-bottom: 12px; display: inline-flex; align-items: center; gap: 6px; background-color: rgba(16, 185, 129, 0.1); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.2); padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
            Grounded: ${currentQ.source_reference}
          </div>
        ` : ''}
        <div class="quiz-question-text">${currentQ.question}</div>
        
        <div class="quiz-options-list">
          ${currentQ.options.map((option, idx) => {
            let optionClass = "";
            if (isAnswered) {
              optionClass = "disabled";
              // Highlight selected answer
              if (idx === state.quizState.selectedOptionIndex) {
                optionClass += idx === currentQ.correctIndex ? " correct-answer" : " selected-incorrect";
              }
              // Force show correct answer
              if (idx === currentQ.correctIndex && idx !== state.quizState.selectedOptionIndex) {
                optionClass += " correct-answer";
              }
            }
            
            const letter = String.fromCharCode(65 + idx); // A, B, C, D
            return `
              <button class="quiz-option ${optionClass}" data-index="${idx}" ${isAnswered ? 'disabled' : ''}>
                <span class="quiz-option-letter">${letter}</span>
                <span style="font-size: 13.5px; font-weight: 500;">${option}</span>
              </button>
            `;
          }).join('')}
        </div>

        <!-- Explanation box -->
        ${isAnswered ? `
          <div class="quiz-explanation-box">
            <span class="quiz-explanation-title">
              ${state.quizState.selectedOptionIndex === currentQ.correctIndex 
                ? '<span style="color: var(--success);">✓ Correct</span>' 
                : '<span style="color: var(--danger);">✗ Incorrect</span>'
              } — AI Explanation
            </span>
            <p class="quiz-explanation-text">${currentQ.explanation}</p>
          </div>
        ` : ''}

        <!-- Next button -->
        ${isAnswered ? `
          <div style="display:flex; justify-content:flex-end;">
            <button class="btn btn-primary" id="qz-next-btn">
              ${currentIndex + 1 === totalQ ? 'Finish Quiz' : 'Next Question'}
            </button>
          </div>
        ` : ''}
      </div>
    `;

    // Hook option buttons click
    container.querySelectorAll('.quiz-option').forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (!isAnswered) {
          const idx = parseInt(btn.getAttribute('data-index'), 10);
          app.answerQuizQuestion(idx);
        }
      });
    });

    // Hook Next button click
    if (isAnswered) {
      container.querySelector('#qz-next-btn').addEventListener('click', () => {
        app.nextQuizQuestion();
      });
    }

    wrapper.appendChild(container);
    return wrapper;
  },

  /**
   * Helper: Formats document text sections with simple headers/lists
   */
  formatDocumentMarkdown: function(text) {
    if (!text) return '';
    let html = text.trim();
    // Render Headings
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    // Render list items
    html = html.replace(/^-\s+(.+)$/gm, '<li>$1</li>');
    // Wrap groups of <li> in <ul>
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    // Parse Bold tags
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Paragraph spaces
    html = html.replace(/\n\n/g, '</p><p>');
    // Return wrapped paragraphs
    return `<p>${html}</p>`;
  },

  /**
   * Helper: Parses standard markdown paragraphs for message bubbles
   */
  parseMarkdownParagraphs: function(text) {
    if (!text) return '';
    let html = text;
    // Bold markup
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Wrap newlines
    html = html.replace(/\n/g, '<br>');
    return html;
  }
};

if (typeof window !== 'undefined') {
  window.Components = Components;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Components;
}
