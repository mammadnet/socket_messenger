// DOM Elements
const loginContainer = document.getElementById('login-container');
const chatContainer = document.getElementById('chat-container');
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username-input');
const usernameDisplay = document.getElementById('username-display');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const logoutButton = document.getElementById('logout-button');
const messagesContainer = document.getElementById('messages-container');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');

// State
let username = '';
let isLoggedIn = false;
let connectionStatus = 'disconnected';
let messageIds = new Set();
let messages = [];
let messagePollingInterval;

// Event Listeners
loginForm.addEventListener('submit', handleLogin);
logoutButton.addEventListener('click', handleLogout);
messageForm.addEventListener('submit', handleSendMessage);

// Check if username is stored in localStorage on initial load
document.addEventListener('DOMContentLoaded', () => {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
        usernameInput.value = storedUsername;
    }
});

// Functions
async function handleLogin(e) {
    e.preventDefault();
    
    username = usernameInput.value.trim();
    if (!username) return;
    
    try {
        // Call the login endpoint
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username })
        });
        
        if (response.ok) {
            // Login successful
            isLoggedIn = true;
            connectionStatus = 'connected';
            
            // Update UI
            loginContainer.style.display = 'none';
            chatContainer.style.display = 'flex';
            usernameDisplay.textContent = username;
            updateConnectionStatus();
            
            // Store username in localStorage
            localStorage.setItem('username', username);
            
            // Start polling for messages
            startMessagePolling();
        } else {
            const data = await response.json();
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('Connection error. Please try again.');
    }
}

async function handleLogout() {
    try {
        // Call the logout endpoint
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username })
        });
        
        if (!response.ok) {
            console.error('Logout failed');
        }
    } catch (error) {
        console.error('Error during logout:', error);
    } finally {
        // Always update the UI state even if the API call fails
        isLoggedIn = false;
        connectionStatus = 'disconnected';
        
        // Update UI
        loginContainer.style.display = 'flex';
        chatContainer.style.display = 'none';
        updateConnectionStatus();
        
        // Stop polling for messages
        stopMessagePolling();
        
        // Clear messages
        messages = [];
        messageIds.clear();
        messagesContainer.innerHTML = '';
    }
}

async function handleSendMessage(e) {
    e.preventDefault();
    
    const messageText = messageInput.value.trim();
    if (!messageText) return;
    
    try {
        const response = await fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                message: messageText
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        // Clear input field
        messageInput.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        connectionStatus = 'error';
        updateConnectionStatus();
    }
}

function startMessagePolling() {
    // Fetch initial messages
    fetchMessages();
    
    // Set up polling every 5 seconds
    messagePollingInterval = setInterval(fetchMessages, 5000);
}

function stopMessagePolling() {
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
        messagePollingInterval = null;
    }
}

async function fetchMessages() {
    try {
        const response = await fetch('/messages');
        if (response.ok) {
            const data = await response.json();
            
            // Filter out duplicate messages
            const newMessages = data.filter(msg => !messageIds.has(msg.id));
            
            if (newMessages.length > 0) {
                console.log(`Adding ${newMessages.length} new messages`);
                
                // Add new messages to the state
                messages = [...messages, ...newMessages];
                
                // Update the message IDs set
                newMessages.forEach(msg => messageIds.add(msg.id));
                
                // Update the UI
                renderMessages(newMessages);
            }
            
            connectionStatus = 'connected';
            updateConnectionStatus();
        } else {
            connectionStatus = 'error';
            updateConnectionStatus();
        }
    } catch (error) {
        console.error('Error fetching messages:', error);
        connectionStatus = 'error';
        updateConnectionStatus();
    }
}

function renderMessages(newMessages) {
    newMessages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.user === username ? 'sent' : 'received'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const usernameElement = document.createElement('span');
        usernameElement.className = 'username';
        usernameElement.textContent = message.user;
        
        const textElement = document.createElement('p');
        textElement.className = 'text';
        textElement.textContent = message.message;
        
        const timeElement = document.createElement('span');
        timeElement.className = 'time';
        timeElement.textContent = message.time;
        
        messageContent.appendChild(usernameElement);
        messageContent.appendChild(textElement);
        messageContent.appendChild(timeElement);
        
        messageElement.appendChild(messageContent);
        
        messagesContainer.appendChild(messageElement);
    });
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateConnectionStatus() {
    statusIndicator.className = `status-indicator ${connectionStatus}`;
    
    switch (connectionStatus) {
        case 'connected':
            statusText.textContent = 'Connected';
            break;
        case 'connecting':
            statusText.textContent = 'Connecting...';
            break;
        case 'error':
            statusText.textContent = 'Connection Error';
            break;
        default:
            statusText.textContent = 'Disconnected';
    }
} 