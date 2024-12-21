# app.py
from flask import Flask, render_template, request, jsonify
import requests
import json
from threading import Thread
import time

app = Flask(__name__)

# Configuration for Ollama API
OLLAMA_API_URL = "http://localhost:11434"

def get_available_models():
    """Fetch available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
    except requests.exceptions.RequestException:
        return []
    return []

def generate_response(model, prompt, personality):
    """Generate response from specified model"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'model': model,
            'prompt': f"{personality}\n\nUser: {prompt}",
            'stream': False
        }
        response = requests.post(f"{OLLAMA_API_URL}/api/generate", 
                               headers=headers, 
                               json=data)
        if response.status_code == 200:
            return response.json().get('response', '')
    except requests.exceptions.RequestException:
        return "Error generating response"
    return "Error generating response"

@app.route('/')
def home():
    """Render the main page"""
    models = get_available_models()
    return render_template('index.html', models=models)

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    """Start the conversation between two models"""
    data = request.json
    model1 = data.get('model1')
    model2 = data.get('model2')
    personality1 = data.get('personality1')
    personality2 = data.get('personality2')
    initial_prompt = "Hello! Let's have a conversation."
    
    # Generate first response
    response = generate_response(model1, initial_prompt, personality1)
    
    return jsonify({
        'status': 'success',
        'message': response
    })

@app.route('/continue_conversation', methods=['POST'])
def continue_conversation():
    """Continue the conversation with the next model's response"""
    data = request.json
    current_model = data.get('current_model')
    personality = data.get('personality')
    previous_message = data.get('previous_message')
    
    response = generate_response(current_model, previous_message, personality)
    
    return jsonify({
        'status': 'success',
        'message': response
    })

if __name__ == '__main__':
    app.run(debug=True)