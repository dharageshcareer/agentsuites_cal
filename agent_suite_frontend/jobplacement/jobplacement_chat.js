document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const clearChatButton = document.getElementById('clear-chat');
    const initialMessage = document.getElementById('initial-message').cloneNode(true);

    // Backend API endpoint from your README.md
    const API_URL = 'http://127.0.0.1:8000/api/jobplacement_rag/chat';

    // Function to scroll to the bottom of the chat window
    const scrollToBottom = () => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    // Function to add a message to the chat window
    const addMessage = (message, sender) => {
        const messageElement = document.createElement('div');
        
        // Add base message class
        messageElement.classList.add('message');

        if (sender === 'user') {
            // User message styling (right-aligned)
            messageElement.classList.add('message-user');
        } else {
            // Bot message styling (left-aligned)
            messageElement.classList.add('message-bot');
        }

        // To render newlines correctly, we can't use textContent directly.
        // A simple replacement of newlines with <br> tags is a safe way to preserve formatting.
        messageElement.innerHTML = message.replace(/\n/g, '<br>');
        chatWindow.appendChild(messageElement);
        scrollToBottom();
    };

    // Function to show a typing indicator
    const showTypingIndicator = () => {
        const typingElement = document.createElement('div');
        typingElement.id = 'typing-indicator';
        typingElement.classList.add('message', 'message-bot');
        typingElement.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatWindow.appendChild(typingElement);
        scrollToBottom();
    };

    // Function to remove the typing indicator
    const removeTypingIndicator = () => {
        document.getElementById('typing-indicator')?.remove();
    };

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMessage = messageInput.value.trim();

        if (userMessage) {
            // Add user message to chat
            addMessage(userMessage, 'user');
            // Clear the input
            messageInput.value = '';
            
            // Show typing indicator while waiting for the response
            showTypingIndicator();

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_prompt: userMessage }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                removeTypingIndicator();

                // Check if the expected 'response' key exists in the data
                const botResponse = data.response;
                if (botResponse) {
                    addMessage(botResponse, 'bot');
                } else {
                    throw new Error("The API response format is incorrect. Expected { 'response': '...' }.");
                }

            } catch (error) {
                removeTypingIndicator();
                console.error('Error fetching from API:', error);
                // Provide a more helpful error message
                const errorMessage = 'Sorry, something went wrong. Please ensure the backend server is running and there are no CORS issues. Check the browser console for more details.';
                addMessage(errorMessage, 'bot');
            }
        }
    });

    // Handle clear chat button click
    clearChatButton.addEventListener('click', () => {
        // Remove all messages from the chat window
        while (chatWindow.firstChild) {
            chatWindow.removeChild(chatWindow.firstChild);
        }
        // Add the initial greeting message back
        chatWindow.appendChild(initialMessage);
        scrollToBottom();
    });

    // Ensure chat starts scrolled to the bottom if there's overflow initially
    scrollToBottom();
});