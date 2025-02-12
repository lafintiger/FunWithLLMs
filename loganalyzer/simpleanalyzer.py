import gradio as gr
import requests
import json
from datetime import datetime
import os
from scapy.all import rdpcap
import tempfile

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            return models
        return ["No models found"]
    except:
        return ["Error connecting to Ollama"]

def analyze_file(file, selected_model, analysis_instructions):
    """Analyze uploaded file using selected Ollama model"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_output_{timestamp}.txt"
    
    # Read file content based on type
    if file.name.endswith('.pcap'):
        # Process PCAP file
        try:
            packets = rdpcap(file.name)
            file_content = "\n".join([str(packet.summary()) for packet in packets[:100]])  # Limit to first 100 packets
        except Exception as e:
            return f"Error processing PCAP file: {str(e)}", None
    else:
        # Process text file
        try:
            with open(file.name, 'r') as f:
                file_content = f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}", None

    # Prepare system prompt
    system_prompt = """You are an expert log and network traffic analyzer with deep knowledge of cyber security. 
    Analyze the provided logs or network traffic for potential security issues, anomalies, or indicators of compromise.
    Focus on identifying suspicious patterns, potential attacks, and security relevant events.
    Provide detailed analysis with specific findings and recommendations."""

    # Prepare message for the model
    user_message = f"""
    Analysis Instructions: {analysis_instructions}
    
    File Content:
    {file_content}
    
    Please provide a detailed analysis focusing on the specified instructions."""

    # Call Ollama API
    try:
        response = requests.post('http://localhost:11434/api/generate',
            json={
                "model": selected_model,
                "system": system_prompt,
                "prompt": user_message
            },
            stream=True
        )
        
        # Process streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line.decode('utf-8'))
                if 'response' in json_response:
                    full_response += json_response['response']
                    
        # Save output to file
        with open(output_file, 'w') as f:
            f.write(f"Analysis Timestamp: {timestamp}\n")
            f.write(f"Selected Model: {selected_model}\n")
            f.write(f"Analysis Instructions: {analysis_instructions}\n\n")
            f.write("Analysis Results:\n")
            f.write(full_response)
            
        return full_response, output_file
        
    except Exception as e:
        error_msg = f"Error communicating with Ollama: {str(e)}"
        with open(output_file, 'w') as f:
            f.write(f"Error: {error_msg}")
        return error_msg, output_file

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Cyber Threat Analysis Interface") as interface:
        gr.Markdown("# Cyber Threat Analysis Interface")
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(label="Upload PCAP or Text File")
                model_dropdown = gr.Dropdown(
                    choices=get_available_models(),
                    label="Select Analysis Model",
                    value=get_available_models()[0] if get_available_models() else None
                )
                analysis_input = gr.Textbox(
                    label="Analysis Instructions",
                    placeholder="Enter specific instructions for analysis (e.g., 'Look for potential SQL injection attempts')",
                    lines=3
                )
                analyze_button = gr.Button("Analyze")
                
            with gr.Column():
                output_text = gr.Textbox(label="Analysis Results", lines=20)
                file_output = gr.File(label="Download Analysis Report")
                
        analyze_button.click(
            fn=analyze_file,
            inputs=[file_input, model_dropdown, analysis_input],
            outputs=[output_text, file_output]
        )
        
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=False)