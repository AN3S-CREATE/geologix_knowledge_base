/**
 * GeoLogix AI - Shared Utilities
 * Common functions used across all UI variants
 * Version: 1.0.0
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    API_BASE_URL: (() => {
        // Detect if we're running through ngrok or locally
        const currentHost = window.location.host;
        if (currentHost.includes('ngrok') || currentHost.includes('ngrok-free')) {
            // Running through ngrok - use the same host for API
            return `${window.location.protocol}//${currentHost}/api`;
        } else {
            // Running locally - use localhost
            return 'http://localhost:8000/api';
        }
    })(),
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    SUPPORTED_FILE_TYPES: [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain',
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/png',
        'image/jpeg',
        'image/jpg'
    ],
    VOICE_RECOGNITION_LANG: 'en-US'
};

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Send a chat message to the AI
 */
async function sendChatMessage(message, conversationId = null) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                chat_id: conversationId,
                conversation_id: conversationId
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Chat API error:', error);
        return {
            success: false,
            error: error.message,
            response: 'Sorry, I encountered an error. Please make sure the backend server is running.'
        };
    }
}

/**
 * Upload a file to the knowledge base
 */
async function uploadFile(file, onProgress = null) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();

        return new Promise((resolve, reject) => {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && onProgress) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', `${CONFIG.API_BASE_URL}/upload`);
            xhr.send(formData);
        });
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

/**
 * Search the knowledge base
 */
async function searchKnowledge(query, filters = {}) {
    try {
        const params = new URLSearchParams({
            q: query,
            ...filters
        });

        const response = await fetch(`${CONFIG.API_BASE_URL}/search?${params}`);

        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Search error:', error);
        return {
            success: false,
            error: error.message,
            results: []
        };
    }
}

/**
 * Get knowledge base statistics
 */
async function getKnowledgeStats() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/stats`);

        if (!response.ok) {
            throw new Error(`Stats failed: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Stats error:', error);
        return {
            success: false,
            total_items: 0,
            categories: {}
        };
    }
}

/**
 * Check system health
 */
async function checkHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        return false;
    }
}

// ============================================================================
// VOICE RECOGNITION
// ============================================================================

class VoiceRecognition {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.onResult = null;
        this.onError = null;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = CONFIG.VOICE_RECOGNITION_LANG;

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (this.onResult) {
                    this.onResult(transcript);
                }
                this.isListening = false;
            };

            this.recognition.onerror = (event) => {
                console.error('Voice recognition error:', event.error);
                if (this.onError) {
                    this.onError(event.error);
                }
                this.isListening = false;
            };

            this.recognition.onend = () => {
                this.isListening = false;
            };
        }
    }

    start() {
        if (this.recognition && !this.isListening) {
            this.recognition.start();
            this.isListening = true;
            return true;
        }
        return false;
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    isAvailable() {
        return this.recognition !== null;
    }
}

// ============================================================================
// FILE HANDLING
// ============================================================================

/**
 * Validate file before upload
 */
function validateFile(file) {
    // Check file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        return {
            valid: false,
            error: `File size exceeds maximum (${formatFileSize(CONFIG.MAX_FILE_SIZE)})`
        };
    }

    // Check file type
    if (!CONFIG.SUPPORTED_FILE_TYPES.includes(file.type)) {
        return {
            valid: false,
            error: 'Unsupported file type'
        };
    }

    return { valid: true };
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Get file icon based on file type
 */
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': '📕',
        'doc': '📘',
        'docx': '📘',
        'txt': '📄',
        'csv': '📊',
        'xls': '📊',
        'xlsx': '📊',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'gif': '🖼️'
    };
    return iconMap[ext] || '📄';
}

// ============================================================================
// UI UTILITIES
// ============================================================================

/**
 * Format timestamp for display
 */
function formatTimestamp(date = new Date()) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * Format relative time (e.g., "2 minutes ago")
 */
function formatRelativeTime(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced with a notification library
    console.log(`[${type.toUpperCase()}] ${message}`);

    // You can implement a toast notification here
    // For now, using console.log
}

/**
 * Auto-resize textarea as user types
 */
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================================================
// MARKDOWN RENDERING (Basic)
// ============================================================================

/**
 * Convert basic markdown to HTML
 */
function renderMarkdown(text) {
    let html = escapeHtml(text);

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code blocks
    html = html.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');

    // Inline code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    // Lists (basic)
    html = html.replace(/^- (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    return html;
}

// ============================================================================
// STORAGE UTILITIES
// ============================================================================

/**
 * Save to local storage
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error('Local storage error:', error);
        return false;
    }
}

/**
 * Load from local storage
 */
function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (error) {
        console.error('Local storage error:', error);
        return defaultValue;
    }
}

// ============================================================================
// EXPORT FOR USE IN OTHER SCRIPTS
// ============================================================================

// Make functions available globally
window.GeoLogixAPI = {
    sendChatMessage,
    uploadFile,
    searchKnowledge,
    getKnowledgeStats,
    checkHealth
};

window.GeoLogixUtils = {
    VoiceRecognition,
    validateFile,
    formatFileSize,
    getFileIcon,
    formatTimestamp,
    formatRelativeTime,
    escapeHtml,
    showNotification,
    autoResizeTextarea,
    debounce,
    renderMarkdown,
    saveToLocalStorage,
    loadFromLocalStorage
};

// ============================================================================
// INITIALIZATION
// ============================================================================

// Check backend health on load
document.addEventListener('DOMContentLoaded', async () => {
    const isHealthy = await checkHealth();
    if (!isHealthy) {
        console.warn('⚠️ Backend server is not responding. Make sure it is running on http://localhost:8000');
    } else {
        console.log('✅ Backend server is healthy');
    }
});

console.log('✅ GeoLogix AI Shared Utilities loaded');
