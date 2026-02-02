document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const chatView = document.getElementById('chat-view');
    const searchView = document.getElementById('search-view');
    const uploadView = document.getElementById('upload-view');

    const views = {
        chat: chatView,
        search: searchView,
        upload: uploadView
    };

    const setView = (viewName) => {
        navItems.forEach((btn) => btn.classList.toggle('active', btn.dataset.view === viewName));
        Object.entries(views).forEach(([name, el]) => {
            if (!el) return;
            el.classList.toggle('active', name === viewName);
        });
    };

    navItems.forEach((btn) => {
        btn.addEventListener('click', () => setView(btn.dataset.view));
    });

    const knowledgeCountEl = document.getElementById('knowledge-count');
    const refreshStats = async () => {
        if (!knowledgeCountEl) return;
        const stats = await window.GeoLogixAPI.getKnowledgeStats();
        if (stats && typeof stats.total_items === 'number') {
            knowledgeCountEl.textContent = stats.total_items;
        } else {
            knowledgeCountEl.textContent = '0';
        }
    };

    refreshStats();

    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('light-mode');
        });
    }

    const chatDisplay = document.getElementById('chat-display');
    const chatInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn-chat');
    const uploadBtnChat = document.getElementById('upload-btn-chat');

    let conversationId = null;

    const scrollChatToBottom = () => {
        if (!chatDisplay) return;
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    };

    const addChatMessage = (text, sender) => {
        if (!chatDisplay) return;

        const msg = document.createElement('div');
        msg.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerText = sender === 'user' ? 'YOU' : 'AI';

        const content = document.createElement('div');
        content.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerText = text;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        const now = new Date();
        timeDiv.innerText = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

        content.appendChild(textDiv);
        content.appendChild(timeDiv);
        msg.appendChild(avatar);
        msg.appendChild(content);
        chatDisplay.appendChild(msg);
        scrollChatToBottom();
    };

    const sendChat = async () => {
        const text = (chatInput && chatInput.value ? chatInput.value : '').trim();
        if (!text) return;

        addChatMessage(text, 'user');
        chatInput.value = '';
        sendBtn.disabled = true;

        try {
            const result = await window.GeoLogixAPI.sendChatMessage(text, conversationId);
            if (result && result.chat_id) {
                conversationId = result.chat_id;
            }
            addChatMessage((result && result.response) ? result.response : 'No response received.', 'ai');
        } catch (err) {
            addChatMessage(`Error: ${err.message || err}`, 'ai');
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
            refreshStats();
        }
    };

    if (sendBtn) sendBtn.addEventListener('click', sendChat);
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }

    const vr = new window.GeoLogixUtils.VoiceRecognition();
    if (voiceBtn) {
        if (vr.isAvailable()) {
            vr.onResult = (transcript) => {
                chatInput.value = transcript;
                chatInput.focus();
            };
            voiceBtn.addEventListener('click', () => {
                if (vr.isListening) {
                    vr.stop();
                } else {
                    vr.start();
                }
            });
        } else {
            voiceBtn.disabled = true;
        }
    }

    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const filterChips = document.querySelectorAll('.filter-chip');
    const searchResults = document.getElementById('search-results');

    let currentFilter = 'all';

    filterChips.forEach((chip) => {
        chip.addEventListener('click', () => {
            filterChips.forEach((c) => c.classList.remove('active'));
            chip.classList.add('active');
            currentFilter = chip.dataset.filter || 'all';
        });
    });

    const renderSearchResults = (results, query) => {
        if (!searchResults) return;

        searchResults.innerHTML = '';

        if (!results || results.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'results-placeholder';
            empty.innerHTML = `<div class="placeholder-icon">🔍</div><p>No results for "${window.GeoLogixUtils.escapeHtml(query)}"</p>`;
            searchResults.appendChild(empty);
            return;
        }

        results.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'result-row';

            const title = item.filename || item.subject || item.relative_path || 'Unknown';
            const type = item.type || 'item';

            const titleEl = document.createElement('div');
            titleEl.className = 'result-title';
            titleEl.innerText = title;

            const metaEl = document.createElement('div');
            metaEl.className = 'result-meta';
            metaEl.innerText = type;

            row.appendChild(titleEl);
            row.appendChild(metaEl);
            searchResults.appendChild(row);
        });
    };

    const runSearch = async () => {
        const q = (searchInput && searchInput.value ? searchInput.value : '').trim();
        if (!q) return;

        if (searchResults) {
            searchResults.innerHTML = '<div class="results-placeholder"><div class="placeholder-icon">⏳</div><p>Searching...</p></div>';
        }

        const result = await window.GeoLogixAPI.searchKnowledge(q, { source: currentFilter, limit: 25 });
        const resultsArray = Array.isArray(result) ? result : (result && Array.isArray(result.results) ? result.results : []);
        renderSearchResults(resultsArray, q);
    };

    if (searchBtn) searchBtn.addEventListener('click', runSearch);
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                runSearch();
            }
        });
    }

    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const uploadList = document.getElementById('upload-list');

    const renderUploadItem = (file) => {
        const row = document.createElement('div');
        row.className = 'upload-item';

        const name = document.createElement('div');
        name.className = 'upload-name';
        name.innerText = file.name;

        const status = document.createElement('div');
        status.className = 'upload-status';
        status.innerText = 'Queued';

        const bar = document.createElement('div');
        bar.className = 'upload-bar';
        const fill = document.createElement('div');
        fill.className = 'upload-fill';
        fill.style.width = '0%';
        bar.appendChild(fill);

        row.appendChild(name);
        row.appendChild(status);
        row.appendChild(bar);

        return { row, status, fill };
    };

    const handleFiles = async (fileList) => {
        const files = Array.from(fileList || []);
        for (const file of files) {
            const validation = window.GeoLogixUtils.validateFile(file);
            if (!validation.valid) {
                if (uploadList) {
                    const errRow = document.createElement('div');
                    errRow.className = 'upload-item error';
                    errRow.innerText = `${file.name}: ${validation.error || 'Invalid file'}`;
                    uploadList.appendChild(errRow);
                }
                continue;
            }

            const ui = uploadList ? renderUploadItem(file) : null;
            if (ui) uploadList.appendChild(ui.row);

            try {
                if (ui) ui.status.innerText = 'Uploading...';
                const result = await window.GeoLogixAPI.uploadFile(file, (pct) => {
                    if (ui) ui.fill.style.width = `${pct.toFixed(0)}%`;
                });
                if (ui) ui.status.innerText = (result && result.status === 'saved') ? 'Complete' : 'Failed';
            } catch (err) {
                if (ui) ui.status.innerText = `Error: ${err.message || err}`;
            }
        }
        refreshStats();
    };

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
            fileInput.value = '';
        });
    }

    if (uploadBtnChat && fileInput) {
        uploadBtnChat.addEventListener('click', () => {
            setView('upload');
            fileInput.click();
        });
    }

    setView('chat');
});
