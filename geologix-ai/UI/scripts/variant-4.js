document.addEventListener('DOMContentLoaded', () => {
    const navTabs = document.querySelectorAll('.nav-tab');
    const overviewTab = document.getElementById('overview-tab');
    const knowledgeTab = document.getElementById('knowledge-tab');
    const analyticsTab = document.getElementById('analytics-tab');
    const chatTab = document.getElementById('chat-tab');

    const panels = {
        overview: overviewTab,
        knowledge: knowledgeTab,
        analytics: analyticsTab,
        chat: chatTab
    };

    const setTab = (name) => {
        navTabs.forEach((btn) => btn.classList.toggle('active', btn.dataset.tab === name));
        Object.entries(panels).forEach(([tabName, el]) => {
            if (!el) return;
            el.classList.toggle('active', tabName === name);
        });
    };

    navTabs.forEach((btn) => {
        btn.addEventListener('click', () => setTab(btn.dataset.tab));
    });

    const metricKnowledge = document.getElementById('metric-knowledge');
    const metricEmails = document.getElementById('metric-emails');
    const metricDocs = document.getElementById('metric-docs');

    const catEmails = document.getElementById('cat-emails');
    const catDocs = document.getElementById('cat-docs');
    const catKb = document.getElementById('cat-kb');
    const catAttach = document.getElementById('cat-attach');

    const refreshStats = async () => {
        const stats = await window.GeoLogixAPI.getKnowledgeStats();
        const categories = (stats && stats.categories) ? stats.categories : {};

        if (metricKnowledge) metricKnowledge.innerText = (stats && typeof stats.total_items === 'number') ? stats.total_items : '--';
        if (metricEmails) metricEmails.innerText = (typeof categories.emails === 'number') ? categories.emails : '--';
        if (metricDocs) metricDocs.innerText = (typeof categories.documents === 'number') ? categories.documents : '--';

        if (catEmails) catEmails.innerText = (typeof categories.emails === 'number') ? `${categories.emails} items` : '-- items';
        if (catDocs) catDocs.innerText = (typeof categories.documents === 'number') ? `${categories.documents} items` : '-- items';
        if (catKb) catKb.innerText = (typeof categories.knowledge === 'number') ? `${categories.knowledge} items` : '-- items';

        const attachCount = (typeof categories.attachments === 'number')
            ? categories.attachments
            : (typeof categories.archives === 'number' ? categories.archives : null);

        if (catAttach) catAttach.innerText = (typeof attachCount === 'number') ? `${attachCount} items` : '-- items';
    };

    refreshStats();

    const uploadAction = document.getElementById('upload-action');
    const searchAction = document.getElementById('search-action');
    const analyzeAction = document.getElementById('analyze-action');
    const chatAction = document.getElementById('chat-action');

    const fileInput = document.getElementById('file-input');

    if (uploadAction && fileInput) {
        uploadAction.addEventListener('click', () => {
            fileInput.click();
        });
    }

    if (searchAction) {
        searchAction.addEventListener('click', () => {
            setTab('knowledge');
            const kbSearch = document.getElementById('kb-search');
            if (kbSearch) kbSearch.focus();
        });
    }

    if (analyzeAction) {
        analyzeAction.addEventListener('click', () => {
            setTab('chat');
        });
    }

    if (chatAction) {
        chatAction.addEventListener('click', () => {
            setTab('chat');
        });
    }

    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }

    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');

    let conversationId = null;

    const addChatMessage = (text, sender) => {
        if (!chatMessages) return;

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
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
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

    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files && e.target.files[0];
            if (!file) return;

            const validation = window.GeoLogixUtils.validateFile(file);
            if (!validation.valid) {
                addChatMessage(validation.error || 'Invalid file.', 'ai');
                fileInput.value = '';
                return;
            }

            addChatMessage(`Uploading ${file.name}...`, 'ai');

            try {
                const result = await window.GeoLogixAPI.uploadFile(file);
                if (result && result.status === 'saved') {
                    addChatMessage(`Upload complete: ${file.name}`, 'ai');
                } else {
                    addChatMessage(`Upload failed: ${file.name}`, 'ai');
                }
            } catch (err) {
                addChatMessage(`Upload error: ${err.message || err}`, 'ai');
            } finally {
                fileInput.value = '';
                refreshStats();
            }
        });
    }

    const kbSearch = document.getElementById('kb-search');
    const knowledgeList = document.getElementById('knowledge-list');

    const renderKnowledgeList = (items) => {
        if (!knowledgeList) return;
        knowledgeList.innerHTML = '';

        if (!items || items.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'list-placeholder';
            empty.innerText = 'No results';
            knowledgeList.appendChild(empty);
            return;
        }

        items.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'kb-row';

            const title = document.createElement('div');
            title.className = 'kb-title';
            title.innerText = item.filename || item.subject || item.relative_path || 'Unknown';

            const meta = document.createElement('div');
            meta.className = 'kb-meta';
            meta.innerText = item.type || 'item';

            row.appendChild(title);
            row.appendChild(meta);
            knowledgeList.appendChild(row);
        });
    };

    const runKbSearch = window.GeoLogixUtils.debounce(async () => {
        const q = (kbSearch && kbSearch.value ? kbSearch.value : '').trim();
        if (!q) {
            if (knowledgeList) {
                knowledgeList.innerHTML = '<div class="list-placeholder">Search or select a category to view items</div>';
            }
            return;
        }

        const result = await window.GeoLogixAPI.searchKnowledge(q, { source: 'all', limit: 25 });
        const resultsArray = Array.isArray(result) ? result : (result && Array.isArray(result.results) ? result.results : []);
        renderKnowledgeList(resultsArray);
    }, 300);

    if (kbSearch) kbSearch.addEventListener('input', runKbSearch);

    setTab('overview');
});
