document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatDisplay = document.getElementById('chat-display');
    const cmdInput = document.querySelector('.cmd-input');
    const submitBtn = document.querySelector('.input-submit');
    const navBtns = document.querySelectorAll('.nav-btn');
    const fileListContainer = document.querySelector('.file-list'); // For dynamic updates

    const apiBaseUrl = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL)
        ? CONFIG.API_BASE_URL
        : 'http://localhost:8000/api';
    let conversationId = null;

    // Create hidden file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Upload Button Handler
    const uploadBtn = document.querySelector('button[title="Upload File"]');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        addMessage(`Uploading ${file.name}...`, 'system');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.status === 'saved') {
                addMessage(`Upload complete: ${file.name} saved to storage.`, 'system');
                // Could refresh file list here logic
            } else {
                addMessage('Upload failed.', 'system');
            }
        } catch (err) {
            console.error(err);
            addMessage('Error Uploading File.', 'system');
        }
        fileInput.value = ''; // Reset
    });

    // Utility: Auto-scroll to bottom of chat
    const scrollToBottom = () => {
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    };

    // Handler: User Input
    const handleInput = async () => {
        const text = cmdInput.value.trim();
        if (!text) return;

        // 1. Add User Message
        addMessage(text, 'user');
        cmdInput.value = '';
        cmdInput.disabled = true; // Prevent double submit

        // 2. Send to Backend
        try {
            const response = await fetch(`${apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    chat_id: conversationId,
                    conversation_id: conversationId,
                    model: "geologix-core-v1"
                })
            });

            const data = await response.json();

            if (data && data.chat_id) {
                conversationId = data.chat_id;
            }

            // 3. Display Response
            if (data.response) {
                addMessage(data.response, 'system');
            }

            // 4. Handle Data Visualization (if data returned)
            if (data.data && Array.isArray(data.data)) {
                renderDataResults(data.data);
            }

        } catch (error) {
            console.error('API Error:', error);
            addMessage("SYSTEM ERROR: Connection to Geologix Core failed. Ensure server is running.", 'system');
        } finally {
            cmdInput.disabled = false;
            cmdInput.focus();
        }
    };

    // Function: Add Message to DOM
    const addMessage = (text, sender) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender === 'system' ? 'system-message' : 'user-message'}`;

        // Style user messages differently
        if (sender === 'user') {
            msgDiv.style.alignSelf = 'flex-end';
            msgDiv.style.background = 'rgba(70, 92, 107, 0.3)';
            msgDiv.style.border = '1px solid var(--color-steel-blue)';
            msgDiv.style.padding = '1rem';
            msgDiv.style.maxWidth = '60%';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'msg-content';
        contentDiv.innerText = text;

        const metaDiv = document.createElement('div');
        metaDiv.className = 'msg-meta';
        const now = new Date();
        metaDiv.innerText = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

        if (sender === 'system') {
            const headerDiv = document.createElement('div');
            headerDiv.className = 'msg-header';
            headerDiv.innerText = 'GEO-LOGIX CORE';
            msgDiv.appendChild(headerDiv);
        }

        msgDiv.appendChild(contentDiv);
        msgDiv.appendChild(metaDiv);
        chatDisplay.appendChild(msgDiv);
        scrollToBottom();
    };

    // Event Listeners
    submitBtn.addEventListener('click', handleInput);

    cmdInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleInput();
        }
    });

    // Nav Toggle Interaction
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Helper: Visualize Results in Right Panel
    const renderDataResults = (results) => {
        if (!fileListContainer) return;

        fileListContainer.innerHTML = ''; // Clear current

        results.forEach(item => {
            const li = document.createElement('li');
            li.className = 'file-item';

            let icon = '📄';
            let tag = 'DOC';

            if (item.type === 'email') {
                icon = '📧';
                tag = 'MAIL';
            }

            // Truncate name if too long
            const name = item.filename || item.subject || 'Unknown';
            const displayName = name.length > 25 ? name.substring(0, 22) + '...' : name;

            li.innerHTML = `
                <span class="file-icon">${icon}</span>
                <span class="file-name" title="${name}">${displayName}</span>
                <span class="file-tag">${tag}</span>
            `;
            fileListContainer.appendChild(li);
        });

        // Add flash effect to panel
        const panel = document.querySelector('.right-panel');
        if (panel) {
            panel.style.transition = 'box-shadow 0.2s';
            panel.style.boxShadow = '0 0 20px var(--color-electric-lime)';
            setTimeout(() => panel.style.boxShadow = 'none', 500);
        }
    };

    // Focus input on load
    cmdInput.focus();
});
