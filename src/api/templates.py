"""
HTML Templates for Chat Interface
"""


def get_chat_html() -> str:
    """Get the chat interface HTML"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Chat - AI Teacher</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #ffffff;
            --primary-dark: #e5e5e5;
            --secondary: #d4d4d4;
            --accent: #a3a3a3;
            --success: #ffffff;
            --warning: #d4d4d4;
            --background: #000000;
            --surface: #1a1a1a;
            --surface-light: #2a2a2a;
            --text: #ffffff;
            --text-secondary: #a3a3a3;
            --border: #404040;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--background);
            background-image: 
                radial-gradient(at 0% 0%, rgba(255, 255, 255, 0.03) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(255, 255, 255, 0.02) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(255, 255, 255, 0.03) 0px, transparent 50%),
                radial-gradient(at 0% 100%, rgba(255, 255, 255, 0.02) 0px, transparent 50%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow: hidden;
        }
        
        .container {
            width: 100%;
            max-width: 900px;
            height: 92vh;
            background: rgba(26, 26, 26, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.05),
                inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }
        
        .header {
            background: #000000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            position: relative;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 30px;
            gap: 30px;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 24px;
            flex: 1;
        }
        
        .header-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            border-right: 1px solid rgba(255, 255, 255, 0.15);
            padding-right: 24px;
        }
        
        .brand-icon {
            font-size: 24px;
        }
        
        .brand-text h1 {
            font-size: 16px;
            font-weight: 600;
            margin: 0;
            color: white;
            line-height: 1.2;
        }
        
        .brand-text .tagline {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.5);
            font-weight: 400;
        }
        
        .header-stats {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-icon {
            font-size: 14px;
        }
        
        .stat-text {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .stat-label {
            font-size: 9px;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 12px;
            color: white;
            font-weight: 600;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: rgba(34, 197, 94, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            animation: statusPulse 2s ease-in-out infinite;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
        }
        
        .status-text {
            font-size: 11px;
            color: #22c55e;
            font-weight: 600;
        }
        
        @keyframes statusPulse {
            0%, 100% { 
                opacity: 1; 
                box-shadow: 0 0 8px rgba(34, 197, 94, 0.6), 0 0 0 0 rgba(34, 197, 94, 0.4);
            }
            50% { 
                opacity: 0.8; 
                box-shadow: 0 0 12px rgba(34, 197, 94, 0.8), 0 0 0 8px rgba(34, 197, 94, 0);
            }
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .progress-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .circular-progress {
            position: relative;
            width: 50px;
            height: 50px;
        }
        
        .circular-progress svg {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }
        
        .circular-progress-bg {
            fill: none;
            stroke: rgba(255, 255, 255, 0.1);
            stroke-width: 3;
        }
        
        .circular-progress-fill {
            fill: none;
            stroke: #ffffff;
            stroke-width: 3;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
        }
        
        .circular-progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: 700;
            color: var(--primary);
        }
        
        .progress-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .progress-label {
            font-size: 11px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .progress-details {
            font-size: 10px;
            color: var(--text-secondary);
            opacity: 0.7;
        }
        
        .ai-progress {
            display: none;
            margin-left: 48px;
            margin-bottom: 12px;
        }
        
        .ai-progress.active {
            display: block;
        }
        
        .ai-progress-bar {
            width: 200px;
            height: 4px;
            background: var(--surface);
            border-radius: 2px;
            overflow: hidden;
            border: 1px solid var(--border);
        }
        
        .ai-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ffffff, #a3a3a3);
            border-radius: 2px;
            animation: aiProgress 2s ease-in-out infinite;
        }
        
        @keyframes aiProgress {
            0% { width: 0%; transform: translateX(0); }
            50% { width: 70%; transform: translateX(0); }
            100% { width: 100%; transform: translateX(0); }
        }
        
        .info-value {
            color: var(--primary);
            font-weight: 600;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            background: var(--background);
            scroll-behavior: smooth;
        }
        
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: transparent;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: var(--surface-light);
            border-radius: 4px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: var(--border);
        }
        
        .message {
            margin-bottom: 24px;
            display: flex;
            animation: messageSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(20px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-wrapper {
            display: flex;
            gap: 12px;
            max-width: 75%;
            align-items: flex-end;
        }
        
        .message.user .message-wrapper {
            flex-direction: row-reverse;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .message.user .avatar {
            background: linear-gradient(135deg, #ffffff, #d4d4d4);
        }
        
        .message.assistant .avatar {
            background: linear-gradient(135deg, #a3a3a3, #737373);
        }
        
        .message-bubble {
            padding: 14px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.6;
            font-size: 15px;
            position: relative;
        }
        
        .message.user .message-bubble {
            background: linear-gradient(135deg, #ffffff, #e5e5e5);
            color: #000000;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
        }
        
        .message.assistant .message-bubble {
            background: var(--surface);
            color: var(--text);
            border-bottom-left-radius: 4px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        /* Markdown styling */
        .message-bubble.markdown h3 {
            color: var(--primary);
            font-size: 16px;
            font-weight: 600;
            margin: 12px 0 8px 0;
        }
        
        .message-bubble.markdown strong {
            color: var(--primary);
            font-weight: 600;
        }
        
        .message-bubble.markdown em {
            color: var(--secondary);
            font-style: italic;
        }
        
        .message-bubble.markdown code {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            color: var(--primary);
        }
        
        .message-bubble.markdown pre {
            background: var(--background);
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 8px 0;
            border: 1px solid var(--border);
        }
        
        .message-bubble.markdown pre code {
            background: transparent;
            padding: 0;
            color: var(--text);
        }
        
        .message-bubble.markdown ul,
        .message-bubble.markdown ol {
            margin: 8px 0;
            padding-left: 24px;
        }
        
        .message-bubble.markdown li {
            margin: 4px 0;
        }
        
        .message-bubble.markdown blockquote {
            border-left: 3px solid var(--primary);
            padding-left: 12px;
            margin: 8px 0;
            color: var(--text-secondary);
            font-style: italic;
        }
        
        .message-bubble.markdown p {
            margin: 8px 0;
        }
        
        .message-bubble.markdown a {
            color: var(--primary);
            text-decoration: none;
            border-bottom: 1px solid var(--primary);
        }
        
        .message-bubble.markdown a:hover {
            color: var(--secondary);
            border-bottom-color: var(--secondary);
        }
        
        .message.system .message-bubble {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 100%;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            padding: 10px 16px;
        }
        
        .typing-indicator {
            display: none;
            margin-left: 48px;
            margin-bottom: 20px;
        }
        
        .typing-indicator.active {
            display: block;
        }
        
        .typing-bubble {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 14px 18px;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            width: fit-content;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .typing-dots {
            display: flex;
            gap: 6px;
            align-items: center;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary);
            animation: typingBounce 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }
        
        @keyframes typingBounce {
            0%, 60%, 100% { 
                transform: translateY(0);
                opacity: 0.7;
            }
            30% { 
                transform: translateY(-10px);
                opacity: 1;
            }
        }
        
        .quick-actions {
            padding: 16px 30px;
            background: var(--surface);
            border-top: 1px solid var(--border);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .quick-action-btn {
            padding: 10px 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--primary);
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .quick-action-btn:hover {
            background: var(--primary);
            color: #000000;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
            border-color: var(--primary);
        }
        
        .input-container {
            padding: 20px 30px 24px;
            background: var(--surface);
            border-top: 1px solid var(--border);
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        .input-wrapper {
            flex: 1;
            position: relative;
        }
        
        #userInput {
            width: 100%;
            padding: 14px 20px;
            background: var(--background);
            border: 2px solid var(--border);
            border-radius: 16px;
            font-size: 15px;
            color: var(--text);
            outline: none;
            transition: all 0.3s;
            font-family: 'Inter', sans-serif;
            resize: none;
        }
        
        #userInput:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
        }
        
        #userInput::placeholder {
            color: var(--text-secondary);
        }
        
        .send-button {
            padding: 14px 28px;
            background: linear-gradient(135deg, #ffffff, #d4d4d4);
            color: #000000;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .send-button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 255, 255, 0.3);
        }
        
        .send-button:active:not(:disabled) {
            transform: translateY(0);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        @media (max-width: 768px) {
            .container {
                height: 100vh;
                border-radius: 0;
                max-width: 100%;
            }
            
            .header-content {
                flex-direction: column;
                padding: 12px 16px;
                gap: 12px;
            }
            
            .header-left {
                flex-direction: column;
                width: 100%;
                gap: 12px;
            }
            
            .header-brand {
                border-right: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.15);
                padding-right: 0;
                padding-bottom: 12px;
            }
            
            .brand-icon {
                font-size: 20px;
            }
            
            .brand-text h1 {
                font-size: 14px;
            }
            
            .brand-text .tagline {
                font-size: 9px;
            }
            
            .header-stats {
                flex-wrap: wrap;
                gap: 8px;
                width: 100%;
            }
            
            .stat-item {
                flex: 1;
                min-width: calc(50% - 4px);
                padding: 8px 10px;
            }
            
            .stat-icon {
                font-size: 12px;
            }
            
            .stat-label {
                font-size: 8px;
            }
            
            .stat-value {
                font-size: 11px;
            }
            
            .header-right {
                flex-direction: row-reverse;
                justify-content: space-between;
                width: 100%;
                gap: 12px;
            }
            
            .status-indicator {
                flex-shrink: 0;
                padding: 5px 12px;
            }
            
            .status-dot {
                width: 6px;
                height: 6px;
            }
            
            .status-text {
                font-size: 10px;
            }
            
            .progress-section {
                align-self: flex-start;
            }
            
            .circular-progress {
                width: 40px;
                height: 40px;
            }
            
            .circular-progress-text {
                font-size: 10px;
            }
            
            .progress-label {
                font-size: 10px;
            }
            
            .progress-details {
                font-size: 9px;
            }
            
            .message-wrapper {
                max-width: 85%;
            }
            
            .message-bubble {
                font-size: 14px;
                padding: 12px 16px;
            }
            
            .quick-actions {
                padding: 12px 16px;
                gap: 8px;
            }
            
            .quick-action-btn {
                font-size: 12px;
                padding: 8px 14px;
            }
            
            .input-container {
                padding: 12px 16px;
            }
            
            #userInput {
                padding: 12px 16px;
                font-size: 14px;
            }
            
            .send-button {
                padding: 12px 20px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <div class="header-brand">
                        <span class="brand-icon">🎓</span>
                        <div class="brand-text">
                            <h1>AI Teaching Assistant</h1>
                            <div class="tagline">Powered by LangGraph & GPT-4</div>
                        </div>
                    </div>
                    
                    <div class="header-stats">
                        <div class="stat-item">
                            <span class="stat-icon">👤</span>
                            <div class="stat-text">
                                <div class="stat-label">User</div>
                                <div class="stat-value" id="userName">Guest</div>
                            </div>
                        </div>
                        
                        <div class="stat-item">
                            <span class="stat-icon">📚</span>
                            <div class="stat-text">
                                <div class="stat-label">Lesson</div>
                                <div class="stat-value" id="lessonTitle">Loading...</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="header-right">
                    <div class="status-indicator">
                        <div class="status-dot"></div>
                        <span class="status-text" id="status">Connected</span>
                    </div>
                    
                    <div class="progress-section">
                        <div class="circular-progress">
                            <svg viewBox="0 0 36 36">
                                <circle class="circular-progress-bg" cx="18" cy="18" r="16"></circle>
                                <circle class="circular-progress-fill" id="progressCircle" cx="18" cy="18" r="16"
                                    stroke-dasharray="100 100" stroke-dashoffset="100"></circle>
                            </svg>
                            <div class="circular-progress-text" id="progressPercent">0%</div>
                        </div>
                        <div class="progress-info">
                            <span class="progress-label">Learning Progress</span>
                            <span class="progress-details" id="progressDetails">0 of 10 lessons</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message system">
                <div class="message-wrapper">
                    <div class="message-bubble">
                        👋 Welcome! Please enter your name to start learning with AI.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="ai-progress" id="aiProgress">
            <div class="ai-progress-bar">
                <div class="ai-progress-fill"></div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-bubble">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
        
        <div class="quick-actions">
            <button class="quick-action-btn" onclick="sendQuickMessage('Explain the main concept')">
                📚 Explain
            </button>
            <button class="quick-action-btn" onclick="sendQuickMessage('Give me an example')">
                💡 Example
            </button>
            <button class="quick-action-btn" onclick="sendQuickMessage('Start quiz')">
                📝 Take Quiz
            </button>
            <button class="quick-action-btn" onclick="sendQuickMessage('Summary')">
                📋 Summary
            </button>
        </div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Type your message here..." 
                       onkeypress="handleKeyPress(event)" autocomplete="off">
            </div>
            <button class="send-button" onclick="sendMessage()" id="sendBtn">
                <span>Send</span>
                <span>→</span>
            </button>
        </div>
    </div>

    <script>
        let ws = null;
        let userName = null;
        let currentLessonId = 1;
        let totalLessons = 10; // Adjust based on your course
        let completedLessons = 0;

        function updateProgress(completed, total) {
            completedLessons = completed;
            totalLessons = total || 10;
            const percentage = Math.round((completed / totalLessons) * 100);
            
            // Update circular progress
            const circle = document.getElementById('progressCircle');
            const circumference = 2 * Math.PI * 16; // radius is 16
            const offset = circumference - (percentage / 100) * circumference;
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = offset;
            
            // Update text
            document.getElementById('progressPercent').textContent = percentage + '%';
            document.getElementById('progressDetails').textContent = `${completed} of ${total} lessons`;
        }

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                updateStatus('Connected', true);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleServerMessage(data);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                updateStatus('Connection Error', false);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                updateStatus('Reconnecting...', false);
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function updateStatus(text, isConnected) {
            const statusEl = document.getElementById('status');
            const statusDot = document.querySelector('.status-dot');
            const statusIndicator = document.querySelector('.status-indicator');
            statusEl.textContent = text;
            if (isConnected) {
                statusDot.style.background = '#22c55e';
                statusDot.style.boxShadow = '0 0 8px rgba(34, 197, 94, 0.6)';
                statusEl.style.color = '#22c55e';
                statusIndicator.style.background = 'rgba(34, 197, 94, 0.1)';
                statusIndicator.style.borderColor = 'rgba(34, 197, 94, 0.3)';
            } else {
                statusDot.style.background = '#ef4444';
                statusDot.style.boxShadow = '0 0 8px rgba(239, 68, 68, 0.6)';
                statusEl.style.color = '#ef4444';
                statusIndicator.style.background = 'rgba(239, 68, 68, 0.1)';
                statusIndicator.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            }
        }

        function handleServerMessage(data) {
            const typingIndicator = document.getElementById('typingIndicator');
            const aiProgress = document.getElementById('aiProgress');
            
            if (data.type === 'user_created') {
                userName = data.user_id;
                currentLessonId = data.current_lesson_id;
                document.getElementById('userName').textContent = userName;
                document.getElementById('lessonTitle').textContent = data.lesson_title || 'Lesson ' + currentLessonId;
                
                // Update progress bar
                const completed = data.completed_lessons ? data.completed_lessons.length : 0;
                updateProgress(completed, totalLessons);
                
                // Restore conversation history
                if (data.conversation_history && data.conversation_history.length > 0) {
                    data.conversation_history.forEach(msg => {
                        const emoji = msg.sender === 'user' ? '👤' : '🤖';
                        const useMarkdown = msg.sender === 'assistant';
                        addMessage(msg.sender, msg.text, emoji, useMarkdown);
                    });
                    addSystemMessage('✨ Previous conversation restored. Continue learning!');
                } else {
                    addSystemMessage('✨ Profile loaded! Ready to learn.');
                }
            } else if (data.type === 'thinking') {
                typingIndicator.classList.add('active');
                aiProgress.classList.add('active');
            } else if (data.type === 'response') {
                typingIndicator.classList.remove('active');
                aiProgress.classList.remove('active');
                addMessage('assistant', data.message, '🤖', true);
            } else if (data.type === 'error') {
                typingIndicator.classList.remove('active');
                addSystemMessage('⚠️ ' + data.message);
            } else if (data.type === 'lesson_update') {
                currentLessonId = data.lesson_id;
                document.getElementById('lessonTitle').textContent = data.lesson_title;
                addSystemMessage('🎉 Great progress! Moving to: ' + data.lesson_title);
            }
        }

        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;

            if (!userName) {
                ws.send(JSON.stringify({
                    type: 'init',
                    user_id: message
                }));
                addMessage('user', message, '👤');
                input.value = '';
                return;
            }

            addMessage('user', message, '👤');
            ws.send(JSON.stringify({
                type: 'message',
                message: message,
                user_id: userName,
                lesson_id: currentLessonId
            }));
            
            input.value = '';
            input.focus();
        }

        function sendQuickMessage(message) {
            if (!userName) {
                addSystemMessage('⚠️ Please enter your name first!');
                document.getElementById('userInput').focus();
                return;
            }
            document.getElementById('userInput').value = message;
            sendMessage();
        }

        function addMessage(sender, text, emoji, useMarkdown = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const wrapper = document.createElement('div');
            wrapper.className = 'message-wrapper';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = emoji;
            
            const bubble = document.createElement('div');
            bubble.className = useMarkdown ? 'message-bubble markdown' : 'message-bubble';
            
            // Render markdown for assistant messages
            if (useMarkdown && typeof marked !== 'undefined') {
                bubble.innerHTML = marked.parse(text);
            } else {
                bubble.textContent = text;
            }
            
            wrapper.appendChild(avatar);
            wrapper.appendChild(bubble);
            messageDiv.appendChild(wrapper);
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addSystemMessage(text) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message system';
            
            const wrapper = document.createElement('div');
            wrapper.className = 'message-wrapper';
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = text;
            
            wrapper.appendChild(bubble);
            messageDiv.appendChild(wrapper);
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Configure marked.js options
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: false,
                mangle: false
            });
        }
        
        // Initialize
        connectWebSocket();
        document.getElementById('userInput').focus();
    </script>
</body>
</html>"""
