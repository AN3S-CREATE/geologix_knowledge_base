document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-display');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');

    let conversationId = null;

    const scrollToBottom = () => {
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    };

    const addMessage = (text, sender) => {
        const msg = document.createElement('div');
        msg.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`;

        const content = document.createElement('div');
        content.className = 'msg-content';
        content.innerText = text;

        msg.appendChild(content);
        chatDisplay.appendChild(msg);
        scrollToBottom();
    };

    const sendMessage = async () => {
        const text = (userInput.value || '').trim();
        if (!text) return;

        addMessage(text, 'user');
        userInput.value = '';
        sendBtn.disabled = true;

        try {
            const result = await window.GeoLogixAPI.sendChatMessage(text, conversationId);
            if (result && result.chat_id) {
                conversationId = result.chat_id;
            }
            addMessage((result && result.response) ? result.response : 'No response received.', 'ai');
        } catch (err) {
            addMessage(`Error: ${err.message || err}`, 'ai');
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    const vr = new window.GeoLogixUtils.VoiceRecognition();
    if (voiceBtn) {
        if (vr.isAvailable()) {
            vr.onResult = (transcript) => {
                userInput.value = transcript;
                userInput.focus();
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

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files && e.target.files[0];
            if (!file) return;

            const validation = window.GeoLogixUtils.validateFile(file);
            if (!validation.valid) {
                addMessage(validation.error || 'Invalid file.', 'ai');
                fileInput.value = '';
                return;
            }

            addMessage(`Uploading ${file.name}...`, 'ai');

            try {
                const result = await window.GeoLogixAPI.uploadFile(file);
                if (result && result.status === 'saved') {
                    addMessage(`Upload complete: ${file.name}`, 'ai');
                } else {
                    addMessage(`Upload failed: ${file.name}`, 'ai');
                }
            } catch (err) {
                addMessage(`Upload error: ${err.message || err}`, 'ai');
            } finally {
                fileInput.value = '';
            }
        });
    }
});
