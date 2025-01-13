const chatContent = document.getElementById('chat-content');
const userInput = document.getElementById('user-input');
const reopenButton = document.getElementById('reopen-button');
const frame = document.getElementById('chatbot-frame');
const dragArea = document.getElementById('drag-area');

let isDragging = false;
let offsetX = 0, offsetY = 0;

// Full-Screen Toggle
function toggleFullScreen() {
    if (frame.style.position === 'fixed') {
        frame.style.position = 'absolute';
        frame.style.top = '10px';
        frame.style.left = '10px';
        frame.style.width = '500px';
        frame.style.height = '500px';
    } else {
        frame.style.position = 'fixed';
        frame.style.top = '0';
        frame.style.left = '0';
        frame.style.width = '100%';
        frame.style.height = '100%';
    }
}

// Close Frame
function closeFrame() {
    frame.style.display = 'none';
    reopenButton.style.display = 'block';
}

// Reopen Frame
function reopenFrame() {
    frame.style.display = 'flex';
    reopenButton.style.display = 'none';
}

// Handle User Input and Send to Backend
async function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        // Display User's Message
        const userMessage = document.createElement('p');
        userMessage.textContent = `You: ${message}`;
        chatContent.appendChild(userMessage);

        // Simulate Bot Response (Replace with actual API request)
        const botResponse = await getBotResponse(message);

        // Display Bot's Response
        const botMessage = document.createElement('p');
        botMessage.textContent = `Bot: ${botResponse}`;
        chatContent.appendChild(botMessage);

        // Clear Input and Scroll to Bottom
        userInput.value = '';
        chatContent.scrollTop = chatContent.scrollHeight;
    }
}

// Simulate Backend Response
async function getBotResponse(userMessage) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(`Echo: ${userMessage}`); // Replace with actual bot response logic
        }, 500);
    });
}

// Dragging Functionality
dragArea.addEventListener('mousedown', (e) => {
    isDragging = true;
    const rect = frame.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    e.preventDefault(); // Prevent text selection
});

document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        frame.style.left = `${e.clientX - offsetX}px`;
        frame.style.top = `${e.clientY - offsetY}px`;
    }
});

document.addEventListener('mouseup', () => {
    isDragging = false;
});
async function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        // Display User's Message
        const userMessage = document.createElement('p');
        userMessage.textContent = `You: ${message}`;
        chatContent.appendChild(userMessage);

        try {
            // Send message to Django backend API
            const response = await fetch('http://127.0.0.1:8000/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();

            // Display Bot's Response
            const botMessage = document.createElement('p');
            if (data.response) {
                botMessage.textContent = `Bot: ${data.response}`;
            } else if (data.error) {
                botMessage.textContent = `Error: ${data.error}`;
            }
            chatContent.appendChild(botMessage);

        } catch (error) {
            const errorMessage = document.createElement('p');
            errorMessage.textContent = `Error: Unable to contact chatbot server.`;
            chatContent.appendChild(errorMessage);
        }

        // Clear Input and Scroll to Bottom
        userInput.value = '';
        chatContent.scrollTop = chatContent.scrollHeight;
    }
}
