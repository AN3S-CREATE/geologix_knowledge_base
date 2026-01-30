document.addEventListener('DOMContentLoaded', () => {
    const modeButtons = document.querySelectorAll('.mode-btn');
    const uploadMode = document.getElementById('upload-mode');
    const analyzeMode = document.getElementById('analyze-mode');
    const chatMode = document.getElementById('chat-mode');

    const modes = {
        upload: uploadMode,
        analyze: analyzeMode,
        chat: chatMode
    };

    const setMode = (name) => {
        modeButtons.forEach((btn) => btn.classList.toggle('active', btn.dataset.mode === name));
        Object.entries(modes).forEach(([modeName, el]) => {
            if (!el) return;
            el.classList.toggle('active', modeName === name);
        });
    };

    modeButtons.forEach((btn) => {
        btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });

    const totalFilesEl = document.getElementById('total-files');
    const totalSizeEl = document.getElementById('total-size');

    const refreshStats = async () => {
        const stats = await window.GeoLogixAPI.getKnowledgeStats();
        if (stats && typeof stats.total_items === 'number' && totalFilesEl) {
            totalFilesEl.textContent = stats.total_items;
        }
        if (totalSizeEl) {
            totalSizeEl.textContent = '--';
        }
    };

    const refreshBtn = document.getElementById('refresh-files');
    if (refreshBtn) refreshBtn.addEventListener('click', refreshStats);

    const fileInput = document.getElementById('file-input');
    const quickUpload = document.getElementById('quick-upload');
    const largeUploadZone = document.getElementById('large-upload-zone');
    const browseBtn = document.getElementById('browse-btn');

    const uploadProgress = document.getElementById('upload-progress');
    const progressPercent = uploadProgress ? uploadProgress.querySelector('.progress-percent') : null;
    const progressFill = uploadProgress ? uploadProgress.querySelector('.progress-fill') : null;
    const progressStatus = uploadProgress ? uploadProgress.querySelector('.progress-status') : null;
    const uploadResults = document.getElementById('upload-results');

    const handleUploadFiles = async (files) => {
        const list = Array.from(files || []);
        if (list.length === 0) return;

        if (uploadProgress) uploadProgress.style.display = 'block';
        if (progressStatus) progressStatus.innerText = 'Uploading...';
        if (uploadResults) uploadResults.innerHTML = '';

        for (let i = 0; i < list.length; i++) {
            const file = list[i];
            const validation = window.GeoLogixUtils.validateFile(file);
            if (!validation.valid) {
                if (uploadResults) {
                    const row = document.createElement('div');
                    row.className = 'upload-result error';
                    row.innerText = `${file.name}: ${validation.error || 'Invalid file'}`;
                    uploadResults.appendChild(row);
                }
                continue;
            }

            try {
                const result = await window.GeoLogixAPI.uploadFile(file, (pct) => {
                    if (progressPercent) progressPercent.innerText = `${pct.toFixed(0)}%`;
                    if (progressFill) progressFill.style.width = `${pct.toFixed(0)}%`;
                });

                if (uploadResults) {
                    const row = document.createElement('div');
                    row.className = 'upload-result';
                    row.innerText = (result && result.status === 'saved')
                        ? `${file.name}: uploaded`
                        : `${file.name}: upload failed`;
                    uploadResults.appendChild(row);
                }
            } catch (err) {
                if (uploadResults) {
                    const row = document.createElement('div');
                    row.className = 'upload-result error';
                    row.innerText = `${file.name}: ${err.message || err}`;
                    uploadResults.appendChild(row);
                }
            }
        }

        if (progressStatus) progressStatus.innerText = 'Done';
        refreshStats();
    };

    const openFilePicker = () => {
        if (fileInput) fileInput.click();
    };

    if (quickUpload) quickUpload.addEventListener('click', openFilePicker);
    if (largeUploadZone) largeUploadZone.addEventListener('click', openFilePicker);
    if (browseBtn) browseBtn.addEventListener('click', openFilePicker);

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleUploadFiles(e.target.files);
            fileInput.value = '';
        });
    }

    const chatDisplay = document.getElementById('chat-display');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');

    let conversationId = null;

    const addChatMessage = (text, sender) => {
        if (!chatDisplay) return;

        const msg = document.createElement('div');
        msg.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.innerText = sender === 'user' ? 'YOU' : 'AI';

        const content = document.createElement('div');
        content.className = 'msg-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'msg-text';
        textDiv.innerText = text;

        content.appendChild(textDiv);
        msg.appendChild(avatar);
        msg.appendChild(content);

        chatDisplay.appendChild(msg);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    };

    const sendChat = async (text) => {
        const msgText = (text || (chatInput && chatInput.value) || '').trim();
        if (!msgText) return;

        addChatMessage(msgText, 'user');
        if (chatInput) chatInput.value = '';
        if (sendBtn) sendBtn.disabled = true;

        try {
            const result = await window.GeoLogixAPI.sendChatMessage(msgText, conversationId);
            if (result && result.chat_id) {
                conversationId = result.chat_id;
            }
            addChatMessage((result && result.response) ? result.response : 'No response received.', 'ai');
        } catch (err) {
            addChatMessage(`Error: ${err.message || err}`, 'ai');
        } finally {
            if (sendBtn) sendBtn.disabled = false;
            if (chatInput) chatInput.focus();
        }
    };

    if (sendBtn) sendBtn.addEventListener('click', () => sendChat());
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

    document.querySelectorAll('.question-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            setMode('chat');
            sendChat(btn.innerText);
        });
    });

    refreshStats();
    setMode('upload');
});
