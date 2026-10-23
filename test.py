import os
import json
import sqlite3
import threading
import time
import logging
from flask import Flask, request, jsonify, render_template_string
import requests # For making requests to the Gemini API

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dual_bot_chat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('dual_bot_chat')

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global database connection and lock
DB_PATH = "dual_bot_chat.db"
db_connection = None
db_lock = threading.Lock()

def get_db_connection():
    """Establishes and returns a SQLite database connection."""
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        db_connection.row_factory = sqlite3.Row # Allows accessing columns by name
    return db_connection

def init_db():
    """Initializes the SQLite database, creating the conversation_state table if it doesn't exist."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation TEXT,
                context TEXT,
                bot1_name TEXT,
                bot2_name TEXT,
                current_speaker TEXT
            )
        """)
        # Initialize with a default row if the table is empty
        cursor.execute("SELECT COUNT(*) FROM conversation_state")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO conversation_state (conversation, context, bot1_name, bot2_name, current_speaker)
                VALUES (?, ?, ?, ?, ?)
            """, (json.dumps([]), "", "TinyLlama", "Qwen", "User"))
        conn.commit()
    logger.info("Database initialized.")

class BotChatManager:
    """Manages the dual bot conversation, context, and interactions with the AI model."""
    def __init__(self):
        self.bot1_name = "TinyLlama"
        self.bot2_name = "Qwen"
        # The API key will be provided by the Canvas environment at runtime if left as an empty string.
        # Do NOT hardcode your API key here for security reasons.
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', "")

    def _call_gemini_api(self, prompt):
        """
        Makes a call to the Gemini API to generate text.
        Args:
            prompt (str): The text prompt for the AI.
        Returns:
            str: The generated text response, or an error message if the call fails.
        """
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + self.gemini_api_key
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            result = response.json()
            if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
                return result['candidates'][0]['content']['parts'][0]['text']
            logger.warning(f"Gemini API returned unexpected structure: {result}")
            return "No response from AI."
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API call failed: {e}")
            return f"Error communicating with AI: {e}"

    def get_bot_response(self, bot_name, current_conversation, current_context):
        """
        Generates a response for a specific bot using the Gemini API.
        The prompt includes the bot's persona, current context, and last message.
        """
        last_message_text = current_conversation[-1]['text'] if current_conversation else ''
        prompt = (
            f"You are {bot_name}. The current conversation context is: \"{current_context}\". "
            f"Previous message: \"{last_message_text}\". "
            "Based on this, provide a concise and engaging response."
        )
        return self._call_gemini_api(prompt)

    def summarize_wikipedia(self, query):
        """
        Simulates a Wikipedia lookup by asking the Gemini API to summarize a topic.
        """
        prompt = f"Summarize the Wikipedia page for \"{query}\" in 2-3 sentences. If you cannot find information, state that."
        summary = self._call_gemini_api(prompt)
        # Check for typical error/no-info messages from the LLM
        if "No response from AI." in summary or "Error communicating with AI:" in summary or "cannot find information" in summary.lower() or "I cannot provide a summary for" in summary.lower():
            return "Could not find relevant Wikipedia information."
        return f"Wikipedia context for \"{query}\": {summary}"

    def get_current_state(self):
        """Retrieves the most recent conversation state from the database."""
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT conversation, context, bot1_name, bot2_name, current_speaker FROM conversation_state ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return {
                    'conversation': json.loads(row['conversation']),
                    'context': row['context'],
                    'bot1Name': row['bot1_name'],
                    'bot2Name': row['bot2_name'],
                    'currentSpeaker': row['current_speaker']
                }
            # Fallback to initial state if no data found (shouldn't happen after init_db)
            return {
                'conversation': [],
                'context': '',
                'bot1Name': self.bot1_name,
                'bot2Name': self.bot2_name,
                'currentSpeaker': "User"
            }

    def update_state(self, conversation, context, current_speaker):
        """Updates the current conversation state in the database."""
        with db_lock:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Always update the latest record. In a multi-user scenario, you'd add a user ID.
            cursor.execute("""
                UPDATE conversation_state
                SET conversation = ?, context = ?, bot1_name = ?, bot2_name = ?, current_speaker = ?
                WHERE id = (SELECT MAX(id) FROM conversation_state)
            """, (json.dumps(conversation), context, self.bot1_name, self.bot2_name, current_speaker))
            conn.commit()

# Initialize the chat manager
manager = BotChatManager()

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main HTML/JavaScript frontend for the chat application."""
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Dual Bot Chat (Python)</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                body { font-family: 'Inter', sans-serif; }
                .chat-message-user {
                    background-color: #3B82F6; /* Blue-500 */
                    color: white;
                    border-bottom-right-radius: 0;
                }
                .chat-message-bot {
                    background-color: #E5E7EB; /* Gray-200 */
                    color: #1F2937; /* Gray-800 */
                    border-bottom-left-radius: 0;
                }
            </style>
        </head>
        <body class="min-h-screen bg-gray-100 flex flex-col items-center p-4 font-inter">
            <h1 class="text-4xl font-bold text-gray-800 mb-6 mt-4">AI Dual Bot Chat</h1>

            <div class="w-full max-w-2xl bg-white rounded-lg shadow-xl p-6 flex flex-col h-[70vh] md:h-[80vh] border border-gray-200">
                <!-- Conversation Area -->
                <div id="conversation-area" class="flex-1 overflow-y-auto mb-4 p-2 space-y-4 rounded-lg bg-gray-50 border border-gray-100">
                    <!-- Messages will be injected here by JavaScript -->
                </div>

                <!-- Context Display -->
                <div id="context-display" class="hidden bg-blue-50 border border-blue-200 text-blue-800 p-3 rounded-lg text-sm mb-4">
                    <span class="font-semibold">Current Context:</span> <span id="current-context-text"></span>
                </div>

                <!-- User Input and Controls -->
                <div class="flex items-center space-x-3 mt-auto">
                    <input
                        type="text"
                        id="user-input"
                        class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                        placeholder="Type your message..."
                    />
                    <button
                        id="send-button"
                        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-5 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Send
                    </button>
                </div>
                <div class="flex justify-between items-center mt-3 space-x-3">
                    <button
                        id="bot-talk-button"
                        class="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-5 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Make Bot Talk
                    </button>
                    <button
                        id="context-button"
                        class="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-5 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Change Context (Wikipedia)
                    </button>
                    <button
                        id="reset-button"
                        class="bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-5 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Reset
                    </button>
                </div>
            </div>

            <!-- Loading Indicator -->
            <div id="loading-indicator" class="mt-4 text-gray-600 hidden">Thinking...</div>

            <!-- Context Modal -->
            <div id="context-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                    <h2 class="text-2xl font-bold mb-4 text-gray-800">Update Conversation Context</h2>
                    <p class="text-gray-600 mb-4">
                        Search Wikipedia to add dynamic context to the conversation.
                    </p>
                    <input
                        type="text"
                        id="search-query-input"
                        class="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200"
                        placeholder="e.g., 'Artificial Intelligence', 'Quantum Physics'"
                    />
                    <div class="flex justify-end space-x-3">
                        <button
                            id="cancel-context-button"
                            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-lg shadow-sm transition duration-200"
                        >
                            Cancel
                        </button>
                        <button
                            id="search-context-button"
                            class="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-200 ease-in-out transform hover:scale-105"
                        >
                            Search & Apply
                        </button>
                    </div>
                </div>
            </div>

            <script>
                const conversationArea = document.getElementById('conversation-area');
                const userInput = document.getElementById('user-input');
                const sendButton = document.getElementById('send-button');
                const botTalkButton = document.getElementById('bot-talk-button');
                const contextButton = document.getElementById('context-button');
                const resetButton = document.getElementById('reset-button');
                const loadingIndicator = document.getElementById('loading-indicator');
                const contextDisplay = document.getElementById('context-display');
                const currentContextText = document.getElementById('current-context-text');
                const contextModal = document.getElementById('context-modal');
                const searchInput = document.getElementById('search-query-input');
                const cancelContextButton = document.getElementById('cancel-context-button');
                const searchContextButton = document.getElementById('search-context-button');

                let currentConversationState = {
                    conversation: [],
                    context: '',
                    bot1Name: 'TinyLlama',
                    bot2Name: 'Qwen',
                    currentSpeaker: 'User'
                };

                const updateUI = () => {
                    conversationArea.innerHTML = ''; // Clear existing messages
                    if (currentConversationState.conversation.length === 0) {
                        conversationArea.innerHTML = '<div class="text-center text-gray-500 italic mt-10">Start the conversation or make the bots talk!</div>';
                    } else {
                        currentConversationState.conversation.forEach(msg => {
                            const messageDiv = document.createElement('div');
                            messageDiv.className = `flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`;
                            messageDiv.innerHTML = `
                                <div class="max-w-[75%] px-4 py-2 rounded-lg shadow ${msg.sender === 'User' ? 'chat-message-user' : 'chat-message-bot'}">
                                    <span class="font-semibold text-sm">${msg.sender}:</span>
                                    <p class="text-base">${msg.text}</p>
                                </div>
                            `;
                            conversationArea.appendChild(messageDiv);
                        });
                    }
                    conversationArea.scrollTop = conversationArea.scrollHeight; // Scroll to bottom

                    if (currentConversationState.context) {
                        contextDisplay.classList.remove('hidden');
                        currentContextText.textContent = currentConversationState.context;
                    } else {
                        contextDisplay.classList.add('hidden');
                        currentContextText.textContent = '';
                    }

                    // Update bot talk button text
                    if (currentConversationState.currentSpeaker !== 'User') {
                         botTalkButton.textContent = `Make ${currentConversationState.currentSpeaker} Talk`;
                    } else {
                         botTalkButton.textContent = `Make Bot Talk`;
                    }
                    // Disable bot talk button if it's the user's turn
                    botTalkButton.disabled = (currentConversationState.currentSpeaker === 'User');
                };

                const showLoading = (isLoading) => {
                    // This function manages the loading indicator and disables/enables buttons
                    loadingIndicator.classList.toggle('hidden', !isLoading);
                    sendButton.disabled = isLoading;
                    botTalkButton.disabled = isLoading || (currentConversationState.currentSpeaker === 'User' && !isLoading);
                    contextButton.disabled = isLoading;
                    resetButton.disabled = isLoading;
                    userInput.disabled = isLoading;
                    searchInput.disabled = isLoading;
                    searchContextButton.disabled = isLoading;
                    cancelContextButton.disabled = isLoading;
                };

                const fetchState = async () => {
                    showLoading(true);
                    try {
                        const response = await fetch('/state');
                        const data = await response.json();
                        currentConversationState = data;
                        updateUI();
                    } catch (error) {
                        console.error('Error fetching state:', error);
                    } finally {
                        showLoading(false);
                    }
                };

                sendButton.addEventListener('click', async () => {
                    const text = userInput.value.trim();
                    if (text) {
                        showLoading(true);
                        try {
                            const response = await fetch('/user_send', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ message: text })
                            });
                            const data = await response.json();
                            currentConversationState = data;
                            userInput.value = '';
                            updateUI();
                        } catch (error) {
                            console.error('Error sending message:', error);
                        } finally {
                            showLoading(false);
                        }
                    }
                });

                userInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendButton.click();
                    }
                });

                botTalkButton.addEventListener('click', async () => {
                    showLoading(true);
                    try {
                        const response = await fetch('/bot_talk', { method: 'POST' });
                        const data = await response.json();
                        currentConversationState = data;
                        updateUI();
                    } catch (error) {
                        console.error('Error making bots talk:', error);
                    } finally {
                        showLoading(false);
                    }
                });

                contextButton.addEventListener('click', () => {
                    searchInput.value = ''; // Clear previous search query
                    contextModal.classList.remove('hidden');
                });

                cancelContextButton.addEventListener('click', () => {
                    contextModal.classList.add('hidden');
                });

                searchContextButton.addEventListener('click', async () => {
                    const query = searchInput.value.trim();
                    if (query) {
                        showLoading(true);
                        try {
                            const response = await fetch('/wikipedia_lookup', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ query: query })
                            });
                            const data = await response.json();
                            currentConversationState = data;
                            updateUI();
                            contextModal.classList.add('hidden');
                        } catch (error) {
                            console.error('Error searching Wikipedia:', error);
                        } finally {
                            showLoading(false);
                        }
                    }
                });

                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        searchContextButton.click();
                    }
                });

                resetButton.addEventListener('click', async () => {
                    showLoading(true);
                    try {
                        const response = await fetch('/reset', { method: 'POST' });
                        const data = await response.json();
                        currentConversationState = data;
                        updateUI();
                    } catch (error) {
                        console.error('Error resetting conversation:', error);
                    } finally {
                        showLoading(false);
                    }
                });

                // Initial fetch of state when page loads
                document.addEventListener('DOMContentLoaded', fetchState);
            </script>
        </body>
        </html>
    """)

@app.route('/state', methods=['GET'])
def get_state():
    """API endpoint to get the current conversation state."""
    state = manager.get_current_state()
    return jsonify(state)

@app.route('/user_send', methods=['POST'])
def user_send_message():
    """
    API endpoint to handle a message sent by the user.
    Adds the user's message and then triggers a response from Bot1 (TinyLlama).
    """
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    state = manager.get_current_state()
    conversation = state['conversation']
    context = state['context']
    bot1_name = state['bot1Name']

    # User speaks
    conversation.append({'sender': 'User', 'text': message})
    manager.update_state(conversation, context, bot1_name) # Set next speaker to bot1

    # Bot1 (TinyLlama) speaks
    bot1_response = manager.get_bot_response(bot1_name, conversation, context)
    conversation.append({'sender': bot1_name, 'text': bot1_response})
    manager.update_state(conversation, context, state['bot2Name']) # Set next speaker to bot2 for subsequent 'bot_talk'

    # Return updated state
    return jsonify(manager.get_current_state())

@app.route('/bot_talk', methods=['POST'])
def bot_talk_next():
    """
    API endpoint to make the bots talk to each other.
    Alternates between Bot1 (TinyLlama) and Bot2 (Qwen).
    """
    state = manager.get_current_state()
    conversation = state['conversation']
    context = state['context']
    bot1_name = state['bot1Name']
    bot2_name = state['bot2Name']
    current_speaker = state['currentSpeaker']

    if current_speaker == bot1_name:
        response = manager.get_bot_response(bot1_name, conversation, context)
        conversation.append({'sender': bot1_name, 'text': response})
        manager.update_state(conversation, context, bot2_name)
    elif current_speaker == bot2_name:
        response = manager.get_bot_response(bot2_name, conversation, context)
        conversation.append({'sender': bot2_name, 'text': response})
        manager.update_state(conversation, context, bot1_name)
    else:
        # This case should ideally not be reached if UI logic is followed,
        # but handles cases where 'User' is current_speaker and bot_talk is clicked.
        return jsonify({'error': 'It is currently the user\'s turn to speak or reset the conversation to initiate bot interaction.'}), 400

    return jsonify(manager.get_current_state())

@app.route('/wikipedia_lookup', methods=['POST'])
def wikipedia_lookup_context():
    """
    API endpoint to perform a Wikipedia lookup and update the conversation context.
    """
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400

    state = manager.get_current_state()
    conversation = state['conversation']
    current_context = manager.summarize_wikipedia(query)
    manager.update_state(conversation, current_context, state['currentSpeaker'])

    return jsonify(manager.get_current_state())

@app.route('/reset', methods=['POST'])
def reset_conversation_state():
    """API endpoint to reset the entire conversation state."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE conversation_state
            SET conversation = ?, context = ?, current_speaker = ?
            WHERE id = (SELECT MAX(id) FROM conversation_state)
        """, (json.dumps([]), "", "User"))
        conn.commit()
    return jsonify(manager.get_current_state())

# Ensure the database is initialized when the Flask application starts.
# This must be called within the application context.
with app.app_context():
    init_db()

if __name__ == '__main__':
    logger.info("Starting Flask Dual Bot Chat server...")
    # Flask typically runs on port 5000 by default.
    # In a Canvas environment, the port might be managed by the platform.
    # For local development, you can explicitly set it: app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000)
