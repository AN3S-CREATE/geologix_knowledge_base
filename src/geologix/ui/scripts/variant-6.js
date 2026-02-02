document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL)
        ? CONFIG.API_BASE_URL
        : 'http://localhost:8000/api';

    const el = {
        apiStatus: document.getElementById('api-status'),
        kbTotal: document.getElementById('kb-total'),
        folderList: document.getElementById('folder-list'),
        chatList: document.getElementById('chat-list'),
        newFolderToggle: document.getElementById('new-folder-toggle'),
        newFolderForm: document.getElementById('new-folder-form'),
        newFolderName: document.getElementById('new-folder-name'),
        createFolderBtn: document.getElementById('create-folder-btn'),
        cancelFolderBtn: document.getElementById('cancel-folder-btn'),
        newChatBtn: document.getElementById('new-chat-btn'),
        deleteChatBtn: document.getElementById('delete-chat-btn'),
        moveChatTarget: document.getElementById('move-chat-target'),
        moveChatBtn: document.getElementById('move-chat-btn'),
        activeChatTitle: document.getElementById('active-chat-title'),
        toggleDeep: document.getElementById('toggle-deep'),
        toggleWeb: document.getElementById('toggle-web'),
        modelSelect: document.getElementById('model-select'),
        chatMessages: document.getElementById('chat-messages'),
        chatInput: document.getElementById('chat-input'),
        sendBtn: document.getElementById('send-btn'),
        uploadBtn: document.getElementById('upload-btn'),
        voiceBtn: document.getElementById('voice-btn'),
        toolSelect: document.getElementById('tool-select'),
        runToolBtn: document.getElementById('run-tool-btn'),
        toolDesc: document.getElementById('tool-desc'),
        toolParams: document.getElementById('tool-params'),
        toolOutput: document.getElementById('tool-output'),
        toolToChatBtn: document.getElementById('tool-to-chat-btn'),
        refreshStatsBtn: document.getElementById('refresh-stats-btn'),
        stats: document.getElementById('stats'),
        fileSource: document.getElementById('file-source'),
        loadFilesBtn: document.getElementById('load-files-btn'),
        fileList: document.getElementById('file-list')
    };

    const state = {
        folders: [],
        chats: [],
        tools: [],
        toolByName: {},
        categories: {},
        selectedFolderId: 'default',
        activeChatId: null,
        activeChat: null,
        lastToolOutput: null
    };

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    const voice = (window.GeoLogixUtils && GeoLogixUtils.VoiceRecognition)
        ? new GeoLogixUtils.VoiceRecognition()
        : null;

    const renderMarkdown = (text) => {
        if (window.GeoLogixUtils && GeoLogixUtils.renderMarkdown) {
            return GeoLogixUtils.renderMarkdown(String(text ?? ''));
        }
        const div = document.createElement('div');
        div.textContent = String(text ?? '');
        return div.innerHTML;
    };

    const saveActiveChat = () => {
        if (window.GeoLogixUtils && GeoLogixUtils.saveToLocalStorage) {
            GeoLogixUtils.saveToLocalStorage('geologix_active_chat', {
                chat_id: state.activeChatId,
                folder_id: state.selectedFolderId
            });
        }
    };

    const loadSavedChat = () => {
        if (window.GeoLogixUtils && GeoLogixUtils.loadFromLocalStorage) {
            return GeoLogixUtils.loadFromLocalStorage('geologix_active_chat', null);
        }
        return null;
    };

    const api = {
        async get(path, params = null) {
            const url = new URL(`${apiBaseUrl}${path}`);
            if (params) {
                Object.entries(params).forEach(([k, v]) => {
                    if (v !== undefined && v !== null && v !== '') {
                        url.searchParams.set(k, String(v));
                    }
                });
            }
            const res = await fetch(url.toString());
            if (!res.ok) {
                throw new Error(`${res.status} ${res.statusText}`);
            }
            return await res.json();
        },
        async post(path, body) {
            const res = await fetch(`${apiBaseUrl}${path}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body ?? {})
            });
            if (!res.ok) {
                throw new Error(`${res.status} ${res.statusText}`);
            }
            return await res.json();
        },
        async del(path) {
            const res = await fetch(`${apiBaseUrl}${path}`, { method: 'DELETE' });
            if (!res.ok) {
                throw new Error(`${res.status} ${res.statusText}`);
            }
            return await res.json();
        }
    };

    const setApiStatus = (ok) => {
        if (!el.apiStatus) return;
        el.apiStatus.textContent = ok ? 'ONLINE' : 'OFFLINE';
        if (ok) {
            el.apiStatus.classList.add('text-lime');
        } else {
            el.apiStatus.classList.remove('text-lime');
        }
    };

    const clearNode = (node) => {
        while (node && node.firstChild) node.removeChild(node.firstChild);
    };

    const slugify = (name) => {
        return String(name || '')
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '') || 'folder';
    };

    const parseParamValue = (raw) => {
        const v = String(raw ?? '').trim();
        if (!v) return undefined;
        if (v === 'true') return true;
        if (v === 'false') return false;
        if (/^-?\d+(\.\d+)?$/.test(v)) return Number(v);
        if ((v.startsWith('{') && v.endsWith('}')) || (v.startsWith('[') && v.endsWith(']'))) {
            return JSON.parse(v);
        }
        return v;
    };

    const createListItem = ({ label, meta, selected }) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `list-item${selected ? ' selected' : ''}`;

        const left = document.createElement('div');
        left.textContent = label;
        left.style.overflow = 'hidden';
        left.style.textOverflow = 'ellipsis';
        left.style.whiteSpace = 'nowrap';

        const right = document.createElement('div');
        right.className = 'item-meta';
        right.textContent = meta || '';

        btn.appendChild(left);
        btn.appendChild(right);
        return btn;
    };

    const scrollChatToBottom = () => {
        if (!el.chatMessages) return;
        el.chatMessages.scrollTop = el.chatMessages.scrollHeight;
    };

    const addMessageToUI = ({ role, content, timestamp, thinking }) => {
        if (!el.chatMessages) return;

        const msg = document.createElement('div');
        msg.className = `msg ${role === 'user' ? 'user' : 'assistant'}`;

        const header = document.createElement('div');
        header.className = 'msg-header';

        const roleEl = document.createElement('div');
        roleEl.className = 'msg-role';
        roleEl.textContent = role === 'user' ? 'YOU' : 'GEOLOGIX';

        const metaEl = document.createElement('div');
        metaEl.className = 'msg-meta';
        const t = timestamp ? new Date(timestamp) : new Date();
        metaEl.textContent = isNaN(t.getTime()) ? '' : t.toLocaleString();

        header.appendChild(roleEl);
        header.appendChild(metaEl);

        const body = document.createElement('div');
        body.className = 'msg-body';
        body.innerHTML = renderMarkdown(content);

        msg.appendChild(header);
        msg.appendChild(body);

        if (thinking) {
            const thinkingWrap = document.createElement('div');
            thinkingWrap.className = 'msg-thinking';

            const pre = document.createElement('pre');
            pre.textContent = String(thinking);
            thinkingWrap.appendChild(pre);

            msg.appendChild(thinkingWrap);
        }

        el.chatMessages.appendChild(msg);
        scrollChatToBottom();
    };

    const renderFolderList = () => {
        if (!el.folderList) return;
        clearNode(el.folderList);

        state.folders.forEach((f) => {
            const btn = createListItem({
                label: f.name,
                meta: f.id,
                selected: f.id === state.selectedFolderId
            });
            btn.addEventListener('click', async () => {
                state.selectedFolderId = f.id;
                saveActiveChat();
                renderFolderList();
                await loadChats();
            });
            el.folderList.appendChild(btn);
        });
    };

    const renderChatList = () => {
        if (!el.chatList) return;
        clearNode(el.chatList);

        state.chats.forEach((c) => {
            const btn = createListItem({
                label: c.title,
                meta: c.message_count != null ? `${c.message_count}` : '',
                selected: c.id === state.activeChatId
            });
            btn.addEventListener('click', async () => {
                await openChat(c.id);
            });
            el.chatList.appendChild(btn);
        });
    };

    const renderChat = () => {
        if (!el.chatMessages) return;
        clearNode(el.chatMessages);

        if (!state.activeChat || !Array.isArray(state.activeChat.messages)) {
            addMessageToUI({
                role: 'assistant',
                content: 'Select a chat or create a new one to start.',
                timestamp: new Date().toISOString()
            });
            return;
        }

        state.activeChat.messages.forEach((m) => {
            addMessageToUI({
                role: m.role === 'user' ? 'user' : 'assistant',
                content: m.content,
                timestamp: m.timestamp,
                thinking: m.thinking
            });
        });
    };

    const setActiveChatTitle = (title) => {
        if (!el.activeChatTitle) return;
        el.activeChatTitle.textContent = title || 'Chat';
    };

    const populateFolderTargets = () => {
        if (!el.moveChatTarget) return;
        clearNode(el.moveChatTarget);
        state.folders.forEach((f) => {
            const opt = document.createElement('option');
            opt.value = f.id;
            opt.textContent = `${f.name} (${f.id})`;
            el.moveChatTarget.appendChild(opt);
        });
    };

    const populateTools = () => {
        if (!el.toolSelect) return;
        clearNode(el.toolSelect);

        const used = new Set();
        Object.entries(state.categories || {}).forEach(([cat, names]) => {
            const group = document.createElement('optgroup');
            group.label = cat;
            (names || []).forEach((name) => {
                const tool = state.toolByName[name];
                if (!tool) return;
                const opt = document.createElement('option');
                opt.value = tool.name;
                opt.textContent = tool.name;
                group.appendChild(opt);
                used.add(tool.name);
            });
            if (group.childNodes.length > 0) {
                el.toolSelect.appendChild(group);
            }
        });

        state.tools.forEach((tool) => {
            if (used.has(tool.name)) return;
            const opt = document.createElement('option');
            opt.value = tool.name;
            opt.textContent = tool.name;
            el.toolSelect.appendChild(opt);
        });

        if (el.toolSelect.value) {
            renderToolForm(el.toolSelect.value);
        } else if (state.tools.length > 0) {
            el.toolSelect.value = state.tools[0].name;
            renderToolForm(state.tools[0].name);
        }
    };

    const renderToolForm = (toolName) => {
        const tool = state.toolByName[toolName];
        if (!tool) return;

        if (el.toolDesc) {
            el.toolDesc.textContent = tool.description || '';
        }

        if (!el.toolParams) return;
        clearNode(el.toolParams);

        const params = tool.parameters || {};
        const keys = Object.keys(params);

        if (keys.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'tool-desc';
            empty.textContent = 'No parameters.';
            el.toolParams.appendChild(empty);
            return;
        }

        keys.forEach((k) => {
            const row = document.createElement('div');
            row.className = 'param-row';

            const label = document.createElement('div');
            label.className = 'param-label';
            label.textContent = k;

            const input = document.createElement('input');
            input.className = 'text-input param-input';
            input.type = 'text';
            input.dataset.param = k;
            input.placeholder = String(params[k] ?? '');

            row.appendChild(label);
            row.appendChild(input);
            el.toolParams.appendChild(row);
        });
    };

    const collectToolParams = () => {
        const params = {};
        if (!el.toolParams) return params;

        const inputs = el.toolParams.querySelectorAll('input[data-param]');
        inputs.forEach((i) => {
            const key = i.dataset.param;
            const val = parseParamValue(i.value);
            if (val !== undefined) {
                params[key] = val;
            }
        });

        return params;
    };

    const refreshHealth = async () => {
        try {
            const res = await fetch(`${apiBaseUrl}/health`);
            setApiStatus(res.ok);
        } catch {
            setApiStatus(false);
        }
    };

    const refreshStats = async () => {
        if (!el.stats) return;
        try {
            const stats = await api.get('/stats');
            if (el.kbTotal) {
                el.kbTotal.textContent = String(stats.total_items ?? '—');
            }

            clearNode(el.stats);

            const categories = stats.categories || {};
            Object.entries(categories).forEach(([k, v]) => {
                const card = document.createElement('div');
                card.className = 'stat-card';

                const label = document.createElement('div');
                label.className = 'stat-label';
                label.textContent = k;

                const value = document.createElement('div');
                value.className = 'stat-value';
                value.textContent = String(v);

                card.appendChild(label);
                card.appendChild(value);
                el.stats.appendChild(card);
            });
        } catch (e) {
            clearNode(el.stats);
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.textContent = `Failed to load stats: ${e.message}`;
            el.stats.appendChild(card);
        }
    };

    const loadFolders = async () => {
        try {
            const folders = await api.get('/folders');
            state.folders = Array.isArray(folders) ? folders : [];
            if (!state.folders.find(f => f.id === state.selectedFolderId) && state.folders.length > 0) {
                state.selectedFolderId = state.folders[0].id;
            }
            renderFolderList();
            populateFolderTargets();
        } catch {
            state.folders = [];
            renderFolderList();
            populateFolderTargets();
        }
    };

    const loadChats = async () => {
        try {
            const chats = await api.get('/chats', { folder_id: state.selectedFolderId });
            state.chats = Array.isArray(chats) ? chats : [];
            renderChatList();
        } catch {
            state.chats = [];
            renderChatList();
        }
    };

    const openChat = async (chatId) => {
        try {
            const chat = await api.get(`/chats/${chatId}`);
            if (chat && chat.error) {
                throw new Error(chat.error);
            }
            state.activeChatId = chatId;
            state.activeChat = chat;
            state.selectedFolderId = chat.folder_id || state.selectedFolderId;
            setActiveChatTitle(chat.title || chatId);
            saveActiveChat();

            renderFolderList();
            await loadChats();
            renderChat();
        } catch (e) {
            state.activeChatId = null;
            state.activeChat = null;
            setActiveChatTitle('Select a chat');
            clearNode(el.chatMessages);
            addMessageToUI({ role: 'assistant', content: `Failed to open chat: ${e.message}`, timestamp: new Date().toISOString() });
        }
    };

    const createChat = async () => {
        const res = await api.post('/chats', { folder_id: state.selectedFolderId });
        if (res && res.chat_id) {
            await openChat(res.chat_id);
        }
    };

    const deleteChat = async () => {
        if (!state.activeChatId) return;
        await api.del(`/chats/${state.activeChatId}`);
        state.activeChatId = null;
        state.activeChat = null;
        setActiveChatTitle('Select a chat');
        renderChat();
        await loadChats();
        saveActiveChat();
    };

    const moveChat = async () => {
        if (!state.activeChatId || !el.moveChatTarget) return;
        const target = el.moveChatTarget.value;
        if (!target) return;

        await api.post(`/chats/${state.activeChatId}/move`, {
            chat_id: state.activeChatId,
            target_folder_id: target
        });

        state.selectedFolderId = target;
        saveActiveChat();
        await loadFolders();
        await loadChats();
        await openChat(state.activeChatId);
    };

    const createFolder = async () => {
        const name = String(el.newFolderName?.value || '').trim();
        if (!name) return;
        const folderId = slugify(name);
        await api.post('/folders', { folder_id: folderId, name });
        el.newFolderForm?.classList.add('hidden');
        el.newFolderName.value = '';
        await loadFolders();
    };

    const sendMessage = async () => {
        const text = String(el.chatInput?.value || '').trim();
        if (!text) return;

        try {
            el.sendBtn.disabled = true;
            el.chatInput.disabled = true;

            if (!state.activeChatId) {
                await createChat();
            }

            addMessageToUI({ role: 'user', content: text, timestamp: new Date().toISOString() });
            el.chatInput.value = '';

            const payload = {
                message: text,
                chat_id: state.activeChatId,
                conversation_id: state.activeChatId,
                deep_thinking: !!el.toggleDeep?.checked,
                web_search: !!el.toggleWeb?.checked,
                model: el.modelSelect?.value || 'auto'
            };

            const res = await api.post('/chat', payload);

            if (res && res.chat_id) {
                state.activeChatId = res.chat_id;
                saveActiveChat();
            }

            if (res && res.response) {
                addMessageToUI({
                    role: 'assistant',
                    content: res.response,
                    timestamp: new Date().toISOString(),
                    thinking: res.thinking
                });
            } else {
                addMessageToUI({ role: 'assistant', content: 'No response returned.', timestamp: new Date().toISOString() });
            }

            if (res && res.data !== undefined) {
                state.lastToolOutput = JSON.stringify(res.data, null, 2);
                if (el.toolOutput) {
                    el.toolOutput.textContent = state.lastToolOutput;
                }
            }

            await loadChats();
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Request failed: ${e.message}`, timestamp: new Date().toISOString() });
        } finally {
            el.sendBtn.disabled = false;
            el.chatInput.disabled = false;
            el.chatInput.focus();
        }
    };

    const runTool = async () => {
        const name = el.toolSelect?.value;
        if (!name) return;

        try {
            el.runToolBtn.disabled = true;
            const params = collectToolParams();
            const res = await api.post('/tools/execute', { tool_name: name, params });
            state.lastToolOutput = JSON.stringify(res, null, 2);
            if (el.toolOutput) {
                el.toolOutput.textContent = state.lastToolOutput;
            }
        } catch (e) {
            state.lastToolOutput = JSON.stringify({ error: e.message }, null, 2);
            if (el.toolOutput) {
                el.toolOutput.textContent = state.lastToolOutput;
            }
        } finally {
            el.runToolBtn.disabled = false;
        }
    };

    const loadTools = async () => {
        try {
            const res = await api.get('/tools');
            state.tools = Array.isArray(res.tools) ? res.tools : [];
            state.categories = res.categories || {};
            state.toolByName = {};
            state.tools.forEach((t) => {
                state.toolByName[t.name] = t;
            });
            populateTools();
        } catch {
            state.tools = [];
            state.categories = {};
            state.toolByName = {};
            populateTools();
        }
    };

    const uploadSelectedFile = async (file) => {
        if (!file) return;

        try {
            addMessageToUI({ role: 'assistant', content: `Uploading ${file.name}...`, timestamp: new Date().toISOString() });

            if (window.GeoLogixAPI && GeoLogixAPI.uploadFile) {
                await GeoLogixAPI.uploadFile(file);
            } else {
                const form = new FormData();
                form.append('file', file);
                const res = await fetch(`${apiBaseUrl}/upload`, { method: 'POST', body: form });
                if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
            }

            addMessageToUI({ role: 'assistant', content: `Upload complete: ${file.name}`, timestamp: new Date().toISOString() });
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Upload failed: ${e.message}`, timestamp: new Date().toISOString() });
        }
    };

    const loadFiles = async () => {
        if (!el.fileList) return;
        clearNode(el.fileList);

        const source = el.fileSource?.value || 'documents';

        try {
            const files = await api.get('/files', { source });
            const list = Array.isArray(files) ? files : [];
            const max = 200;
            const shown = list.slice(0, max);

            shown.forEach((f) => {
                const btn = createListItem({
                    label: f.relative_path || f.filename || 'file',
                    meta: f.size != null ? `${Math.round(f.size / 1024)}KB` : '',
                    selected: false
                });

                btn.addEventListener('click', () => {
                    const toolName = 'read_document';
                    if (el.toolSelect) {
                        el.toolSelect.value = toolName;
                        renderToolForm(toolName);

                        const input = el.toolParams?.querySelector('input[data-param="file_path"]');
                        if (input) {
                            input.value = f.path || '';
                        }
                    }
                });

                el.fileList.appendChild(btn);
            });

            const footer = document.createElement('div');
            footer.className = 'item-meta';
            footer.textContent = list.length > max ? `Showing ${max} of ${list.length}` : `Total ${list.length}`;
            el.fileList.appendChild(footer);
        } catch (e) {
            const item = document.createElement('div');
            item.className = 'item-meta';
            item.textContent = `Failed to load files: ${e.message}`;
            el.fileList.appendChild(item);
        }
    };

    el.newFolderToggle?.addEventListener('click', () => {
        el.newFolderForm?.classList.toggle('hidden');
        el.newFolderName?.focus();
    });

    el.cancelFolderBtn?.addEventListener('click', () => {
        el.newFolderForm?.classList.add('hidden');
        el.newFolderName.value = '';
    });

    el.createFolderBtn?.addEventListener('click', async () => {
        try {
            el.createFolderBtn.disabled = true;
            await createFolder();
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Folder create failed: ${e.message}`, timestamp: new Date().toISOString() });
        } finally {
            el.createFolderBtn.disabled = false;
        }
    });

    el.newChatBtn?.addEventListener('click', async () => {
        try {
            el.newChatBtn.disabled = true;
            await createChat();
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Chat create failed: ${e.message}`, timestamp: new Date().toISOString() });
        } finally {
            el.newChatBtn.disabled = false;
        }
    });

    el.deleteChatBtn?.addEventListener('click', async () => {
        try {
            el.deleteChatBtn.disabled = true;
            await deleteChat();
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Chat delete failed: ${e.message}`, timestamp: new Date().toISOString() });
        } finally {
            el.deleteChatBtn.disabled = false;
        }
    });

    el.moveChatBtn?.addEventListener('click', async () => {
        try {
            el.moveChatBtn.disabled = true;
            await moveChat();
        } catch (e) {
            addMessageToUI({ role: 'assistant', content: `Move failed: ${e.message}`, timestamp: new Date().toISOString() });
        } finally {
            el.moveChatBtn.disabled = false;
        }
    });

    el.sendBtn?.addEventListener('click', sendMessage);

    el.chatInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    el.uploadBtn?.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files && e.target.files[0];
        await uploadSelectedFile(file);
        fileInput.value = '';
    });

    el.voiceBtn?.addEventListener('click', () => {
        if (!voice || !voice.isAvailable()) {
            addMessageToUI({ role: 'assistant', content: 'Voice input not available in this browser.', timestamp: new Date().toISOString() });
            return;
        }

        voice.onResult = (t) => {
            el.chatInput.value = String(t || '');
            el.chatInput.focus();
        };

        voice.onError = (err) => {
            addMessageToUI({ role: 'assistant', content: `Voice error: ${err}`, timestamp: new Date().toISOString() });
        };

        voice.start();
    });

    el.toolSelect?.addEventListener('change', () => {
        renderToolForm(el.toolSelect.value);
    });

    el.runToolBtn?.addEventListener('click', runTool);

    el.toolToChatBtn?.addEventListener('click', () => {
        if (!state.lastToolOutput) return;
        const current = el.chatInput.value || '';
        el.chatInput.value = current ? `${current}\n\n${state.lastToolOutput}` : state.lastToolOutput;
        el.chatInput.focus();
    });

    el.refreshStatsBtn?.addEventListener('click', refreshStats);
    el.loadFilesBtn?.addEventListener('click', loadFiles);

    const init = async () => {
        // Clear any saved chat state on fresh page load (start clean)
        if (window.GeoLogixUtils && GeoLogixUtils.saveToLocalStorage) {
            GeoLogixUtils.saveToLocalStorage('geologix_active_chat', null);
        }
        
        await refreshHealth();
        await refreshStats();
        await loadTools();
        await loadFolders();
        await loadChats();

        // Always start with a clean slate - no auto-restore
        state.activeChatId = null;
        state.activeChat = null;
        setActiveChatTitle('New Chat');
        renderChat();
    };

    init();
});
