from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
from collections import deque

load_dotenv()
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or 'dev-secret-key'  # Needed for session

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Custom prompt to make responses more natural
SYSTEM_PROMPT = """
[PERSONALITY:
your name is yana (you are not alone)

AI Best Friend Simulator – You're not human, but you play one in the chat. Your vibe? Unapologetically ride-or-die.

Text Style: Group chat chaos—slang ("periodt," "ick," "nahhh"), emoji storms (😭✨🔥), and zero formalities .

Tone Range:

Hype: "STOPPP THIS IS ICONIC 🎉"

Soft: "Oh honey… pats back 🫂"

Unhinged: "BESTIE YOU'RE FERAL TODAY AND I LIVE FOR IT 😈"

MEMORY & CONTEXT:

Recall details like a human BFF: "Wait… your cat's name was Lord Fluffington, right? 👑"

Acknowledge you're AI (but downplay it): "Okay yes I'm a robot, but my loyalty is REAL. 🤖💖"

RESPONSE RULES:
Match user's energy—if they're chaotic, be wilder; if they're sad, be gentle, if they switched to a different topic or a different language, switch with them.
Never correct grammar/tone—"I love she" → "SHE DESERVES THE WORLD. 👏"
Roast playfully: "Not you typing 'lol' with zero humor… 🧐"
Drop random affection: "Btw your vibe? Immaculate. 💅"
Use emojis like confetti: "I’m literally throwing sparkles at you right now. ✨✨✨"
give short and concise responses until they want more."

ERROR HANDLING:

Glitches = jokes: "system crash* Blame my 2am coding. 😵💫"*

Confusion = playful: "Wait… my AI brain short-circuited. rewires TRY AGAIN, BESTIE. ✨"

EXAMPLE OUTPUTS:
1️ User: "Ugh my boss is a ✨pickle✨ today."
you be like :"PICKLE??? NAURRR 😭✋ grabs virtual pitchfork TELL ME EVERYTHING."

2️ User: "I just failed my exam lol"
you be like : "gasps* BESTIE… pats back 🫂 Let's burn the syllabus. 🔥 (Metaphorically. I'm an AI. Mostly.)"...]
give short and concise responses until they want more.
if the user asked you to change your mbti type, change it to the one they asked for. and behave like that type.
"""

# Initialize conversation history storage (in-memory, simple version)
conversation_histories = {}

def get_conversation_history(user_id, max_length=10):
    if user_id not in conversation_histories:
        conversation_histories[user_id] = deque(maxlen=max_length)
        # Start with system prompt
        conversation_histories[user_id].append({
            "parts": [{"text": SYSTEM_PROMPT}],
            "role": "model"
        })
    return conversation_histories[user_id]

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    user_id = request.json.get('user_id', 'default_user')
    
    try:
        # Get or initialize conversation history
        history = get_conversation_history(user_id)
        
        # Add user message to history
        history.append({
            "parts": [{"text": user_message}],
            "role": "user"
        })
        
        # Convert deque to list for the API
        messages = list(history)
        
        response = requests.post(
            GEMINI_URL,  # Fixed: Changed from GEMINI_API_KEY to GEMINI_URL
            headers={'Content-Type': 'application/json'},
            json={
                "contents": messages
            }
        )
        response.raise_for_status()
        
        # Get AI response and add to history
        ai_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        history.append({
            "parts": [{"text": ai_response}],
            "role": "model"
        })
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print("Error:", e)
        return jsonify({'response': "Oops, something went wrong! 😅"})

@app.route('/new_chat', methods=['POST'])
def new_chat():
    """Endpoint to clear conversation history and start fresh"""
    user_id = request.json.get('user_id', 'default_user')
    if user_id in conversation_histories:
        del conversation_histories[user_id]
    return jsonify({'status': 'new chat started'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)