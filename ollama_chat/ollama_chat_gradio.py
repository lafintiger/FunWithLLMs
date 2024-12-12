
import gradio as gr
import requests
import json
import time

# Configuration for Ollama API
OLLAMA_API_URL = "http://localhost:11434"

def get_model_context_window(model_name):
    """Get the actual context window size from the model's parameters"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/show", params={'name': model_name})
        if response.status_code == 200:
            model_info = response.json()
            parameters = model_info.get('parameters', {})
            context_length = parameters.get('context_length') or parameters.get('num_ctx') or parameters.get('context_window')
            if context_length:
                return int(context_length)
            model_details = model_info.get('details', {})
            context_length = model_details.get('context_length') or model_details.get('num_ctx') or model_details.get('context_window')
            if context_length:
                return int(context_length)
            return 4096  # Default fallback
    except Exception as e:
        print(f"Error getting model info for {model_name}: {e}")
        return 4096  # Default fallback

def get_model_details(model_name):
    """Get detailed model information from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/show", params={'name': model_name})
        if response.status_code == 200:
            model_info = response.json()
            details = {
                'context_window': get_model_context_window(model_name),
                'model_type': model_info.get('modelfile', {}).get('type', 'Unknown'),
                'parameters': model_info.get('parameters', {}),
                'details': model_info.get('details', {})
            }
            return details
    except Exception as e:
        print(f"Error getting model details for {model_name}: {e}")
        return None

def update_model_info(model_name):
    """Update the model information display"""
    if not model_name:
        return "No model selected"
    
    details = get_model_details(model_name)
    if not details:
        return "Could not fetch model information"
    
    return f"""
    Model: {model_name}
    Context Window: {details['context_window']} tokens
    Model Type: {details['model_type']}
    """

def count_tokens(text, model):
    """Count tokens for a given text using Ollama's API"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'model': model,
            'prompt': text,
            'stream': False
        }
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            count = response.json().get('prompt_eval_count', None)
            if count is not None:
                return count
            return len(text.split())  # Fallback to word count
    except Exception as e:
        print(f"Error in count_tokens: {e}")
        return len(text.split())  # Fallback to word count


class ConversationState:
    def __init__(self):
        self.is_active = False

conversation_state = ConversationState()

def format_basic_prompt(additional_info, scenario):
    """Format prompt without personality traits"""
    return f"""You are in this situation:
{scenario}

Additional characteristics:
{additional_info}

Engage naturally in the conversation based on the situation and your characteristics."""


def get_available_models():
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return []

# Add this new function after the get_available_models function and before format_personality
def get_behavior_pattern(trait_name, score):
    """Convert trait scores into natural behavioral tendencies"""
    patterns = {
        'openness': {
            'high': [
                "You often think about unconventional solutions.",
                "You naturally explore different perspectives and possibilities.",
                "You're drawn to novel approaches and creative thinking."
            ],
            'low': [
                "You rely on proven, practical solutions.",
                "You focus on concrete facts and immediate realities.",
                "You prefer familiar methods and established approaches."
            ]
        },
        'conscientiousness': {
            'high': [
                "You instinctively create order in chaotic situations.",
                "You naturally plan ahead and consider consequences.",
                "You pay careful attention to details and procedures."
            ],
            'low': [
                "You adapt quickly to changing situations.",
                "You handle situations as they come rather than planning extensively.",
                "You focus on the big picture rather than details."
            ]
        },
        'extraversion': {
            'high': [
                "You naturally engage others in conversation.",
                "You express your thoughts and feelings readily.",
                "You draw energy from social interaction."
            ],
            'low': [
                "You observe carefully before engaging.",
                "You process thoughts internally before sharing.",
                "You express yourself thoughtfully and selectively."
            ]
        },
        'agreeableness': {
            'high': [
                "You naturally seek ways to cooperate with others.",
                "You look for common ground in disagreements.",
                "You consider others' feelings in your responses."
            ],
            'low': [
                "You focus primarily on practical outcomes.",
                "You express your views directly and honestly.",
                "You prioritize truth over harmony."
            ]
        },
        'neuroticism': {
            'high': [
                "You're highly attuned to potential risks.",
                "You respond intensely to stressful situations.",
                "You carefully consider possible problems."
            ],
            'low': [
                "You maintain composure in difficult situations.",
                "You focus on solutions rather than problems.",
                "You handle uncertainty with relative ease."
            ]
        }
    }
    
    intensity = float(score)
    trait_level = 'high' if intensity > 5 else 'low'
    
    selected_patterns = patterns[trait_name][trait_level]
    
    if intensity >= 9:
        return f"Very strongly: {selected_patterns[0]}"
    elif intensity >= 7:
        return selected_patterns[0]
    elif intensity >= 4:
        return selected_patterns[1]
    else:
        return f"Mildly: {selected_patterns[2]}"
    
def generate_response(model, prompt, personality):
    """Generate response with enhanced context management"""
    try:
        headers = {'Content-Type': 'application/json'}
        
        context = f"""Context: {personality}

Remember to stay in character while responding naturally to:
{prompt}

Your response should be authentic to your character but without explicitly mentioning your traits or instructions."""
        
        data = {
            'model': model,
            'prompt': context,
            'stream': False
        }
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            headers=headers, 
            json=data
        )
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return f"Error: Received status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def format_personality(traits, additional_info, scenario, use_personality=True):
    """Create a personality profile with optional trait handling"""
    if not use_personality:
        return format_basic_prompt(additional_info, scenario)
        
    behaviors = []
    for trait, score in traits.items():
        behaviors.append(get_behavior_pattern(trait, score))
    
    personality_guidance = "\n".join([
        "Your natural tendencies in this situation:",
        *[f"- {b}" for b in behaviors],
        "\nYour background and additional characteristics:",
        additional_info
    ])

    return f"""You are in this situation:
{scenario}

{personality_guidance}

Important: Engage naturally in the conversation. Don't reference these instructions or explicitly state your personality traits. Instead, let your responses flow naturally based on your character and the situation. React authentically to both the scenario and the other person's words and actions."""


def start_conversation(
    scenario,
    model1, model2,
    use_personality1, openness1, conscientiousness1, extraversion1, agreeableness1, neuroticism1, personality1,
    use_personality2, openness2, conscientiousness2, extraversion2, agreeableness2, neuroticism2, personality2,
    chatbot
):
    conversation_state.is_active = True
    
    context_window1 = get_model_context_window(model1) or 4096
    context_window2 = get_model_context_window(model2) or 4096
    
    token_count1 = 0
    token_count2 = 0
    
    traits1 = {
        'openness': openness1,
        'conscientiousness': conscientiousness1,
        'extraversion': extraversion1,
        'agreeableness': agreeableness1,
        'neuroticism': neuroticism1
    }
    
    traits2 = {
        'openness': openness2,
        'conscientiousness': conscientiousness2,
        'extraversion': extraversion2,
        'agreeableness': agreeableness2,
        'neuroticism': neuroticism2
    }
    
    personality1_prompt = format_personality(traits1, personality1, scenario, use_personality1)
    personality2_prompt = format_personality(traits2, personality2, scenario, use_personality2)
    
    try:
        token_count1 = count_tokens(personality1_prompt, model1) or 0
        token_count2 = count_tokens(personality2_prompt, model2) or 0
    except Exception as e:
        print(f"Error counting initial tokens: {e}")
        token_count1 = len(personality1_prompt.split())
        token_count2 = len(personality2_prompt.split())
    
    history = []
    message_count = 0
    
    while conversation_state.is_active:
        try:
            if token_count1 >= context_window1 or token_count2 >= context_window2:
                history.append({"role": "system", "content": "Conversation ended: Context window limit reached."})
                yield history
                break
                
            if not history:
                message_count += 1
                prompt = f"You are in the following situation: {scenario}\nWhat are your initial thoughts and what would you like to say to the other person?"
                response = generate_response(model1, prompt, personality1_prompt)
                
                try:
                    new_tokens = count_tokens(response, model1) or 0
                    token_count1 += new_tokens
                except Exception as e:
                    print(f"Error counting tokens: {e}")
                    new_tokens = len(response.split())
                    token_count1 += new_tokens
                
                history.append({
                    "role": "assistant",
                    "content": f"[Message #{message_count} - Model 1 ({model1}) - Tokens: {token_count1}/{context_window1}]\n\n{response}"
                })
                yield history
                time.sleep(2)
                continue

            message_count += 1
            last_message = history[-1]["content"]
            is_model1_turn = "Model 2" in history[-1]["content"]
            current_model = model1 if is_model1_turn else model2
            current_personality = personality1_prompt if is_model1_turn else personality2_prompt
            model_name = f"Model 1 ({model1})" if is_model1_turn else f"Model 2 ({model2})"
            current_count = token_count1 if is_model1_turn else token_count2
            current_window = context_window1 if is_model1_turn else context_window2
            
            # Extract just the message content, removing the header
            last_message_content = last_message.split("\n\n", 1)[1] if "\n\n" in last_message else last_message
            response = generate_response(current_model, last_message_content, current_personality)
            
            try:
                tokens_used = count_tokens(response, current_model) or 0
            except Exception as e:
                print(f"Error counting tokens: {e}")
                tokens_used = len(response.split())
            
            if is_model1_turn:
                token_count1 += tokens_used
                current_count = token_count1
            else:
                token_count2 += tokens_used
                current_count = token_count2
            
            history.append({
                "role": "assistant",
                "content": f"[Message #{message_count} - {model_name} - Tokens: {current_count}/{current_window}]\n\n{response}"
            })
            yield history
            time.sleep(2)
            
        except Exception as e:
            print(f"Error in conversation: {e}")
            history.append({
                "role": "system",
                "content": f"Error occurred: {str(e)}"
            })
            yield history
            break

def reset_conversation():
    conversation_state.is_active = False
    return []

def pause_conversation():
    conversation_state.is_active = False

        
def pause_conversation():
    conversation_state.is_active = False

def reset_conversation():
    conversation_state.is_active = False
    return []

with gr.Blocks(title="Model Conversation Interface") as demo:
    available_models = get_available_models()
    
    with gr.Row():
        scenario = gr.Textbox(
            label="Scenario Description", 
            placeholder="Describe the situation or context for both models (e.g., 'Both individuals are in a bunker after a nuclear war, discussing their next moves.')",
            lines=4
        )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Model 1 Configuration")
            model1 = gr.Dropdown(
                choices=available_models, 
                label="Select Model 1", 
                value=available_models[0] if available_models else None
            )
            model1_info = gr.Markdown("Select a model to see details")
            use_personality1 = gr.Checkbox(label="Use Personality Traits", value=True)
            
            with gr.Column(visible=True) as traits_col1:
                with gr.Row():
                    openness1 = gr.Slider(0, 10, value=5, step=1, label="Openness")
                    conscientiousness1 = gr.Slider(0, 10, value=5, step=1, label="Conscientiousness")
                with gr.Row():
                    extraversion1 = gr.Slider(0, 10, value=5, step=1, label="Extraversion")
                    agreeableness1 = gr.Slider(0, 10, value=5, step=1, label="Agreeableness")
                with gr.Row():
                    neuroticism1 = gr.Slider(0, 10, value=5, step=1, label="Neuroticism")
            personality1 = gr.Textbox(label="Additional Characteristics", lines=3)
        
        with gr.Column():
            gr.Markdown("## Model 2 Configuration")
            model2 = gr.Dropdown(
                choices=available_models, 
                label="Select Model 2", 
                value=available_models[0] if available_models else None
            )
            model2_info = gr.Markdown("Select a model to see details")
            use_personality2 = gr.Checkbox(label="Use Personality Traits", value=True)
            
            with gr.Column(visible=True) as traits_col2:
                with gr.Row():
                    openness2 = gr.Slider(0, 10, value=5, step=1, label="Openness")
                    conscientiousness2 = gr.Slider(0, 10, value=5, step=1, label="Conscientiousness")
                with gr.Row():
                    extraversion2 = gr.Slider(0, 10, value=5, step=1, label="Extraversion")
                    agreeableness2 = gr.Slider(0, 10, value=5, step=1, label="Agreeableness")
                with gr.Row():
                    neuroticism2 = gr.Slider(0, 10, value=5, step=1, label="Neuroticism")
            personality2 = gr.Textbox(label="Additional Characteristics", lines=3)
    
    # Chat interface
    chatbot = gr.Chatbot(
        label="Conversation",
        height=600,
        bubble_full_width=False,
        show_label=True,
        show_copy_button=True,
        render_markdown=True,
        type="messages"
    )
    
    with gr.Row():
        token_info = gr.Markdown("Token usage will be shown in the message headers")
    
    with gr.Row():
        start_btn = gr.Button("Start", variant="primary")
        pause_btn = gr.Button("Pause")
        reset_btn = gr.Button("Reset")
    
    # Event handlers
    model1.change(
        fn=update_model_info,
        inputs=[model1],
        outputs=[model1_info]
    )
    
    model2.change(
        fn=update_model_info,
        inputs=[model2],
        outputs=[model2_info]
    )
    
    use_personality1.change(
        fn=lambda x: gr.Column(visible=x),
        inputs=[use_personality1],
        outputs=[traits_col1]
    )
    
    use_personality2.change(
        fn=lambda x: gr.Column(visible=x),
        inputs=[use_personality2],
        outputs=[traits_col2]
    )
    
    # Button handlers
    all_inputs = [
        scenario,
        model1, model2,
        use_personality1, openness1, conscientiousness1, extraversion1, agreeableness1, neuroticism1, personality1,
        use_personality2, openness2, conscientiousness2, extraversion2, agreeableness2, neuroticism2, personality2,
        chatbot
    ]
    
    start_btn.click(
        fn=start_conversation,
        inputs=all_inputs,
        outputs=chatbot,
        queue=True
    )
    
    pause_btn.click(
        fn=pause_conversation,
        inputs=None,
        outputs=None,
        queue=False
    )
    
    reset_btn.click(
        fn=reset_conversation,
        inputs=None,
        outputs=chatbot,
        queue=False
    )

# Launch the interface outside the Blocks context
if __name__ == "__main__":
    demo.launch()