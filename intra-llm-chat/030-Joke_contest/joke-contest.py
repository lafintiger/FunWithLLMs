# pip install gradio ollama-python

import gradio as gr
import random
import ollama
import requests

class JokeCompetition:
    def __init__(self, model_a, model_b):
        self.scores = {"Model A": 0, "Model B": 0}
        self.current_round = 1
        self.model_a = model_a
        self.model_b = model_b
        self.feedback_history = []
        
    def get_joke(self, model_name, is_responding_to=None):
        """Get a joke from the specified model using Ollama"""
        base_prompt = """You are participating in a joke-telling competition against another AI model. Your goal is to tell the most creative, 
        original, and genuinely funny joke possible. The audience will vote on the winner, so make it count! 
        
        Guidelines:
        - Be creative and original
        - Keep it family-friendly
        - Timing and delivery matter
        - You can use wordplay, clever twists, or unexpected endings
        - Avoid common or overused jokes
        - Make it memorable and unique
        
        Your reputation as a comedian is on the line. Show us your best work!"""
        
        # Add feedback history if available
        if self.feedback_history:
            base_prompt += "\n\nHere is some recent feedback from the audience to help you improve:"
            for feedback in self.feedback_history[-3:]:  # Show last 3 pieces of feedback
                base_prompt += f"\n- {feedback}"
            base_prompt += "\n\nPlease consider this feedback when crafting your joke."
        
        if is_responding_to:
            prompt = f"{base_prompt}\n\nYour competitor just told this joke:\n{is_responding_to}\n\nNow it's your turn to tell an even better joke. Just tell the joke without any introduction or commentary."
        else:
            prompt = f"{base_prompt}\n\nYou're going first this round. Tell your best joke without any introduction or commentary."
        
        try:
            response = ollama.generate(model=model_name, prompt=prompt)
            return response.response.strip()
        except Exception as e:
            return f"Error getting joke from {model_name}: {str(e)}"

    def start_round(self, model_a, model_b):
        """Start a new round by randomly selecting which model goes first"""
        self.model_a = model_a
        self.model_b = model_b
        models = ["Model A", "Model B"]
        random.shuffle(models)
        first_model, second_model = models
        
        # Get first joke
        first_model_name = model_a if first_model == "Model A" else model_b
        first_joke = self.get_joke(first_model_name)
        
        # Get second joke, showing the first joke as context
        second_model_name = model_b if second_model == "Model B" else model_a
        second_joke = self.get_joke(second_model_name, first_joke)
        
        round_text = f"Round {self.current_round}\n\n"
        round_text += f"{first_model} ({first_model_name})'s Joke:\n{first_joke}\n\n"
        round_text += f"{second_model} ({second_model_name})'s Joke:\n{second_joke}\n"
        
        return round_text, first_model, second_model

    def add_feedback(self, feedback):
        """Add feedback to the history"""
        if feedback and feedback.strip():
            self.feedback_history.append(feedback.strip())

    def score_round(self, winner, first_model, second_model, feedback=""):
        """Score the round based on user selection and feedback"""
        if winner != "Neither":
            self.scores[winner] += 1
        
        # Add feedback if provided
        self.add_feedback(feedback)
        
        score_text = f"Current Scores:\nModel A: {self.scores['Model A']}\nModel B: {self.scores['Model B']}"
        self.current_round += 1
        
        # Start next round automatically
        next_round_text, next_first, next_second = self.start_round(self.model_a, self.model_b)
        return next_round_text, score_text, next_first, next_second

def get_available_models():
    """Get list of available Ollama models"""
    try:
        # Try direct API call first
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']]
    except:
        try:
            # Fallback to ollama.list()
            models = ollama.list()
            if isinstance(models, dict) and 'models' in models:
                return [model.get('name', 'unknown') for model in models['models']]
        except Exception as e:
            print(f"Error getting models: {str(e)}")
    
    # Final fallback list
    return ["llama2", "mistral", "codellama", "phi", "neural-chat", "starling-lm"]

def create_interface():
    available_models = get_available_models()
    competition = None
    
    def handle_score(winner, first, second, feedback):
        if competition:
            return competition.score_round(winner, first, second, feedback)
        return None, None, None, None
    
    with gr.Blocks() as interface:
        gr.Markdown("# LLM Joke Competition")
        gr.Markdown("To end the competition, simply close this browser tab.")
        
        # Model selection dropdowns
        with gr.Row():
            model_a_dropdown = gr.Dropdown(
                choices=available_models,
                label="Select Model A",
                value=available_models[0] if available_models else None
            )
            model_b_dropdown = gr.Dropdown(
                choices=available_models,
                label="Select Model B",
                value=available_models[1] if len(available_models) > 1 else None
            )
        
        # Hidden state variables
        first_model = gr.State("")
        second_model = gr.State("")
        
        # Display areas
        jokes_display = gr.Textbox(label="Current Round", lines=10, interactive=False)
        scores_display = gr.Textbox(label="Scores", lines=4, interactive=False)
        
        # Control buttons
        with gr.Row():
            start_button = gr.Button("Start Competition", variant="primary")
        
        # Feedback input
        feedback_input = gr.Textbox(
            label="Feedback for the models (what was good/bad about their jokes?)",
            placeholder="Enter your feedback here to help the models improve...",
            lines=2
        )
        
        with gr.Row():
            model_a_button = gr.Button("Model A Won", variant="primary")
            model_b_button = gr.Button("Model B Won", variant="primary")
            neither_button = gr.Button("Neither Won", variant="secondary")
            
        def start_competition(model_a, model_b):
            nonlocal competition
            competition = JokeCompetition(model_a, model_b)
            return competition.start_round(model_a, model_b)
        
        # Event handlers
        start_button.click(
            start_competition,
            inputs=[model_a_dropdown, model_b_dropdown],
            outputs=[jokes_display, first_model, second_model]
        )
        
        model_a_button.click(
            fn=handle_score,
            inputs=[
                gr.State("Model A"),
                first_model,
                second_model,
                feedback_input
            ],
            outputs=[jokes_display, scores_display, first_model, second_model]
        ).then(lambda: "", None, feedback_input)  # Clear feedback after use
        
        model_b_button.click(
            fn=handle_score,
            inputs=[
                gr.State("Model B"),
                first_model,
                second_model,
                feedback_input
            ],
            outputs=[jokes_display, scores_display, first_model, second_model]
        ).then(lambda: "", None, feedback_input)  # Clear feedback after use
        
        neither_button.click(
            fn=handle_score,
            inputs=[
                gr.State("Neither"),
                first_model,
                second_model,
                feedback_input
            ],
            outputs=[jokes_display, scores_display, first_model, second_model]
        ).then(lambda: "", None, feedback_input)  # Clear feedback after use
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()