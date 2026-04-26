document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const themeButton = document.getElementById('theme-button');
    const body = document.body;

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function setTheme(mode) {
        if (mode === 'dark') {
            body.classList.add('dark');
            themeButton.textContent = '☀️';
            themeButton.setAttribute('aria-label', 'Switch to light theme');
        } else {
            body.classList.remove('dark');
            themeButton.textContent = '🌙';
            themeButton.setAttribute('aria-label', 'Switch to dark theme');
        }
        localStorage.setItem('preferredTheme', mode);
    }

    function toggleTheme() {
        const currentTheme = body.classList.contains('dark') ? 'dark' : 'light';
        setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    }

    function sendMessage(questionText) {
        const question = questionText || userInput.value.trim();
        if (question === '') return;

        addMessage(question, true);
        userInput.value = '';

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<span style="opacity: 0.65;">Typing...</span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        })
        .then(response => response.json())
        .then(data => {
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) typingIndicator.remove();
            addMessage(data.answer || 'Sorry, I could not find an answer.');
        })
        .catch(error => {
            console.error('Error:', error);
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) typingIndicator.remove();
            addMessage('Sorry, there was an error processing your request. Please try again.');
        });
    }

    function setupQuickCommands() {
        const quickCommands = document.querySelectorAll('.quick-command');
        quickCommands.forEach((button) => {
            button.addEventListener('click', () => sendMessage(button.textContent));
        });
    }

    sendButton.addEventListener('click', () => sendMessage());
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    themeButton.addEventListener('click', toggleTheme);

    const savedTheme = localStorage.getItem('preferredTheme') || 'light';
    setTheme(savedTheme);

    setupQuickCommands();
    userInput.focus();

    setTimeout(() => {
        addMessage('Welcome to Medical Center Bot! 👋 Ask about our departments, doctors, services, and appointments. Try: "What departments do you have?" or "How to book an appointment?"');
    }, 450);
});