# FunWithLLMs User Guide

## Introduction

FunWithLLMs is an innovative web application that generates conversations between Large Language Models (LLMs) using Ollama. This guide will help you explore AI interactions and create unique dialogues with advanced personality configurations.

## Concept

The application allows you to:
- Select two different AI models
- Assign unique personalities through multiple configuration methods
- Fine-tune personality traits using scientific psychological models
- Watch AI models engage in dynamic, generated conversations

## System Requirements

### Technical Prerequisites
- Python 3.7+
- Ollama installed and configured
- Stable internet connection (for initial setup)
- Modern web browser

### Ollama Setup
1. Download Ollama from: https://ollama.com/
2. Install and run the Ollama application
3. Pull desired models using commands like:
   ```bash
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ```

## Application Setup

### Installation Steps
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Start the Flask application

### Detailed Installation
```bash
# Clone repository
git clone https://github.com/lafintiger/FunWithLLMs.git
cd FunWithLLMs/two-llms-talk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# Or: venv\Scripts\activate  # Windows

# Install dependencies
pip install flask requests

# Run the application
python app.py
```

## Using FunWithLLMs: Personality Configuration

### Model Selection
- Open `http://localhost:5000` in your web browser
- Select two different models from available Ollama models

### Personality Trait Configuration

#### Big Five Personality Traits
The application uses the Five-Factor Model (Big Five) for personality configuration:

1. **Openness**: Measures creativity, curiosity, and willingness to try new things
   - Low (0-4): Practical, traditional
   - High (6-10): Imaginative, adventurous

2. **Conscientiousness**: Reflects organization, discipline, and goal-orientation
   - Low (0-4): Flexible, spontaneous
   - High (6-10): Structured, reliable

3. **Extraversion**: Indicates social interaction and energy levels
   - Low (0-4): Introverted, reserved
   - High (6-10): Outgoing, talkative

4. **Agreeableness**: Measures compassion, cooperation, and empathy
   - Low (0-4): Competitive, critical
   - High (6-10): Sympathetic, kind

5. **Neuroticism**: Reflects emotional stability and sensitivity
   - Low (0-4): Calm, resilient
   - High (6-10): Emotionally reactive, anxious

#### How to Configure
- Use sliders to set each trait's level (0-10)
- Add a free-text description for additional context
- Traits inform how models generate responses

### Conversation Mechanics
1. Choose first model and its personality
2. Choose second model and its personality
3. Click "Start Conversation"
4. Watch models interact dynamically
5. Use "Stop Conversation" to end the dialogue

## Advanced Tips

### Crafting Engaging Personalities
- Be specific and creative in descriptions
- Experiment with trait combinations
- Try contrasting personality settings
- Use role-playing scenarios

## Best Practices
- Start with familiar models
- Use clear, concise personality descriptions
- Observe how different traits interact
- Have fun and be creative!

## Limitations & Considerations
- Conversations are not stored
- Responses are generated in real-time
- AI can produce unexpected results
- Requires local Ollama setup

## Troubleshooting

### Common Issues
- No models listed: Confirm Ollama is running
- Connection errors: Check Ollama API status
- Performance issues: Verify system resources

## Experimental Nature

FunWithLLMs is a creative exploration tool. Conversations may:
- Be unpredictable
- Demonstrate unexpected AI behaviors
- Provide insights into AI interaction dynamics

## Privacy Note
- No external data is collected
- Conversations are not saved
- Entirely local interaction

## Feedback & Community

- Share interesting conversations
- Report bugs on GitHub
- Suggest new features
- Contribute to the project

Enjoy exploring the fascinating world of AI conversations with personality-driven interactions!# FunWithLLMs User Guide

## Introduction

FunWithLLMs is an innovative web application that generates conversations between Large Language Models (LLMs) using Ollama. This guide will help you explore AI interactions and create unique dialogues.

## Concept

The application allows you to:
- Select two different AI models
- Assign unique personalities to each model
- Watch them engage in a dynamic, generated conversation

## System Requirements

### Technical Prerequisites
- Python 3.7+
- Ollama installed and configured
- Stable internet connection (for initial setup)
- Web browser

### Ollama Setup
1. Download Ollama from: https://ollama.com/
2. Install and run the Ollama application
3. Pull desired models using commands like:
   ```bash
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ```

## Application Setup

### Installation Steps
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Start the Flask application

### Detailed Installation
```bash
# Clone repository
git clone https://github.com/lafintiger/FunWithLLMs.git
cd FunWithLLMs/two-llms-talk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# Or: venv\Scripts\activate  # Windows

# Install dependencies
pip install flask requests

# Run the application
python app.py
```

## Using FunWithLLMs

### Model Selection
- Open `http://localhost:5000` in your web browser
- You'll see a list of available Ollama models
- Select two different models for conversation

### Personality Configuration

Personalities add depth and context to AI conversations. Examples:
- Scientific Researcher: "You are a curious scientist exploring complex topics"
- Historical Figure: "Respond as if you're Leonardo da Vinci discussing innovation"
- Fictional Character: "Engage like Sherlock Holmes analyzing a mystery"

### Conversation Mechanics
1. Choose first model and its personality
2. Choose second model and its personality
3. Initiate conversation
4. Watch models interact dynamically

## Advanced Tips

### Crafting Engaging Personalities
- Be specific and creative
- Provide clear context
- Use role-playing scenarios
- Experiment with different combinations

## Best Practices
- Start with familiar models
- Use clear, concise personality descriptions
- Observe how different personalities interact
- Have fun and be creative!

## Limitations & Considerations
- Conversations are not stored
- Responses are generated in real-time
- AI can produce unexpected results
- Requires local Ollama setup

## Troubleshooting

### Common Issues
- No models listed: Confirm Ollama is running
- Connection errors: Check Ollama API status
- Performance issues: Verify system resources

## Experimental Nature

FunWithLLMs is a creative exploration tool. Conversations may:
- Be unpredictable
- Demonstrate unexpected AI behaviors
- Provide insights into AI interaction dynamics

## Privacy Note
- No external data is collected
- Conversations are not saved
- Entirely local interaction

## Feedback & Community

- Share interesting conversations
- Report bugs on GitHub
- Suggest new features
- Contribute to the project

Enjoy exploring the fascinating world of AI conversations!# FunWithLLMs User Guide

## Introduction

FunWithLLMs is an entertaining web application that allows you to create conversations between two Large Language Models (LLMs) using Ollama. This guide will walk you through how to use the application effectively.

## Prerequisites

Before getting started, ensure you have:
- Ollama installed and running
- Python and Flask set up
- The application downloaded and dependencies installed

## Getting Started

### Launching the Application

1. Start the Ollama service
2. Navigate to the project directory
3. Run the application with `python app.py`
4. Open a web browser and go to `http://localhost:5000`

## Using the Application

### Model Selection

1. When you first open the application, you'll see a list of available Ollama models
2. Select two different models for your conversation
   - Model 1 will start the conversation
   - Model 2 will respond to Model 1's message

### Personality Assignment

For each model, you can assign a unique personality:
- Think of a personality trait or role you want the model to adopt
- Examples:
  - A historian discussing world events
  - A poet creating metaphorical responses
  - A scientist explaining complex concepts
  - A comedian making jokes

### Conversation Flow

1. Choose your models
2. Define their personalities
3. Click "Start Conversation"
4. The first model will generate an initial message
5. The second model will respond based on the previous message
6. Continue the conversation as desired

## Tips for Interesting Conversations

- Experiment with different model combinations
- Try contrasting personalities (e.g., optimist vs. pessimist)
- Use specific context or scenario descriptions
- Be creative with personality prompts

## Troubleshooting

### Common Issues
- No models appearing: Ensure Ollama is running
- Errors generating response: Check Ollama configuration
- Web page not loading: Verify Flask is running correctly

## Advanced Usage

- Modify `personality` prompts to create more directed conversations
- Extend the Flask routes to add more sophisticated conversation tracking

## Privacy and Usage Notes

- Conversations are not stored
- Responses are generated in real-time
- Internet connectivity is not required once Ollama is set up

## Feedback and Contributions

- Found a bug? Open an issue on GitHub
- Have an enhancement? Submit a pull request
- Share your most interesting AI conversations!

## Disclaimer

This is an experimental tool. AI models can generate unexpected or inconsistent responses.
