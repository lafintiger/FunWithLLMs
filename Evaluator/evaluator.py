# evaluator.py
#
# Required dependencies:
# pip install gradio pandas requests aiohttp
#
# If you get ModuleNotFoundError, run:
# pip install -r requirements.txt
#
# Make sure Ollama is installed and running locally
# (https://ollama.ai/download)
#
# Usage:
# 1. Install dependencies: pip install gradio pandas requests aiohttp
# 2. Ensure Ollama is running
# 3. Run this script: python evaluator.py
# 4. Access the interface at http://localhost:7860
#
# Session Format:
# ###--- SESSION START ---###
# [commands here]
# ###--- SESSION END ---###

try:
    import gradio as gr
    import pandas as pd
    from datetime import datetime
    import json
    import requests
    import os
    import asyncio
    import aiohttp
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from typing import List, Tuple
    import re
except ModuleNotFoundError as e:
    print(f"\nError: {e}")
    print("\nPlease install missing dependencies using:")
    print("pip install gradio pandas requests aiohttp")
    print("\nOr create requirements.txt with the following content:")
    print("gradio\npandas\nrequests\naiohttp")
    print("\nThen run: pip install -r requirements.txt")
    exit(1)

class AnalysisTool:
    def __init__(self):
        self.history_file = "analysis_history.csv"
        self.ollama_base_url = "http://localhost:11434"
        self.cmd_prompt = """Analyze this command line history from a Red Hat Linux system. Please provide:
1. The apparent goal or task the user was attempting
2. A step-by-step analysis of the commands executed
3. Identification of any errors or inefficiencies
4. Recommendations for improvement or correct approaches
5. Overall success/failure assessment"""
        
        self.vision_prompt = "Please provide a detailed description of what you see in this screenshot."
        
        # Create history file if it doesn't exist
        if not os.path.exists(self.history_file):
            pd.DataFrame(columns=['timestamp', 'analysis_type', 'model', 'input', 'output']
            ).to_csv(self.history_file, index=False)

    def get_installed_models(self):
        """Get list of installed Ollama models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = [model['name'] for model in response.json()['models']]
                return models
            else:
                print(f"Error getting models: {response.status_code}")
                return ["Error fetching models"]
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return ["Error connecting to Ollama"]

    def save_analysis(self, analysis_type, model, input_text, output_text):
        """Save analysis results to CSV"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{
            'timestamp': timestamp,
            'analysis_type': analysis_type,
            'model': model,
            'input': input_text,
            'output': output_text
        }])
        
        history_df = pd.read_csv(self.history_file)
        history_df = pd.concat([history_df, new_row], ignore_index=True)
        history_df.to_csv(self.history_file, index=False)

    def validate_session_markers(self, text: str) -> bool:
        """Validate that session markers are properly formatted"""
        start_pattern = r'###---\s*SESSION\s+START\s*---###'
        end_pattern = r'###---\s*SESSION\s+END\s*---###'
        
        starts = len(re.findall(start_pattern, text))
        ends = len(re.findall(end_pattern, text))
        
        return starts > 0 and starts == ends

    def _split_sessions(self, batch_text):
        """Split batch text into individual sessions"""
        sessions = []
        current_session = []
        
        lines = batch_text.split('\n')
        in_session = False
        
        for line in lines:
            if "###--- SESSION START ---###" in line:
                in_session = True
                current_session = []
            elif "###--- SESSION END ---###" in line:
                in_session = False
                if current_session:
                    sessions.append('\n'.join(current_session))
            elif in_session:
                current_session.append(line)
        
        # Handle case where last session might not have an END marker
        if in_session and current_session:
            sessions.append('\n'.join(current_session))
            
        return sessions

    async def analyze_session(self, session: str, model_name: str, session_num: int) -> Tuple[int, str]:
        """Analyze a single session asynchronously"""
        try:
            async with aiohttp.ClientSession() as session_client:
                async with session_client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"{self.cmd_prompt}\n\nCommand History (Session {session_num}):\n{session}"
                            }
                        ]
                    }
                ) as response:
                    if response.status == 200:
                        content = []
                        async for line in response.content:
                            if line:
                                try:
                                    json_response = json.loads(line)
                                    if 'message' in json_response:
                                        content.append(json_response['message']['content'])
                                except json.JSONDecodeError:
                                    continue
                        
                        result = ''.join(content)
                        self.save_analysis('command', model_name, f"Session {session_num}: {session}", result)
                        return session_num, result
                    else:
                        return session_num, f"Error processing session {session_num}: Status {response.status}"
        except Exception as e:
            return session_num, f"Error processing session {session_num}: {str(e)}"

    async def process_batch(self, sessions: List[str], model_name: str, progress=gr.Progress()) -> str:
        """Process multiple sessions in parallel"""
        tasks = []
        all_results = []
        
        # Create tasks for all sessions
        for i, session in enumerate(sessions, 1):
            task = self.analyze_session(session, model_name, i)
            tasks.append(task)
        
        # Process tasks with progress updates
        total = len(tasks)
        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            session_num, result = await task
            all_results.append((session_num, result))
            progress(i / total, desc=f"Processing session {i}/{total}")
        
        # Sort results by session number and combine
        all_results.sort(key=lambda x: x[0])
        return "\n\n".join([f"=== Analysis for Session {num} ===\n{result}" for num, result in all_results])

    def process_uploaded_file(self, file) -> str:
        """Process uploaded file and return its content"""
        if file is None:
            return ""
        
        try:
            content = file.decode('utf-8')
            if not self.validate_session_markers(content):
                return "Error: Uploaded file must contain properly formatted session markers."
            return content
        except UnicodeDecodeError:
            return "Error: File must be a valid UTF-8 text file."
        except Exception as e:
            return f"Error processing file: {str(e)}"

    def analyze_command_history(self, model_name, command_history, progress=gr.Progress()):
        """Analyze command line history using selected Ollama model"""
        try:
            # First check if we have file upload content
            if isinstance(command_history, bytes):
                command_history = self.process_uploaded_file(command_history)
                if command_history.startswith("Error"):
                    return command_history
            
            # Check if this is a batch upload
            if "###--- SESSION" in command_history:
                if not self.validate_session_markers(command_history):
                    return "Error: Invalid session markers. Please ensure each session starts with '###--- SESSION START ---###' and ends with '###--- SESSION END ---###'"
                
                sessions = self._split_sessions(command_history)
                if not sessions:
                    return "Error: No valid sessions found in input."
                
                # Process sessions asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.process_batch(sessions, model_name, progress))
                return results
            else:
                # Single session analysis
                response = requests.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"{self.cmd_prompt}\n\nCommand History:\n{command_history}"
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    # Handle streaming response
                    full_response = []
                    for line in response.iter_lines():
                        if line:
                            try:
                                json_response = json.loads(line)
                                if 'message' in json_response:
                                    full_response.append(json_response['message']['content'])
                            except json.JSONDecodeError:
                                continue
                    
                    result = ''.join(full_response)
                    # Save analysis
                    self.save_analysis('command', model_name, command_history, result)
                    return result
                else:
                    error_msg = f"Error: Failed to get response from Ollama. Status code: {response.status_code}"
                    if response.text:
                        error_msg += f"\nResponse: {response.text}"
                    return error_msg
                    
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_screenshot(self, model_name, image):
        """Analyze screenshot using selected vision model"""
        try:
            with open(image, "rb") as img_file:
                # Convert image to base64
                import base64
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = requests.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": self.vision_prompt,
                            "images": [image_base64]
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                # Handle streaming response
                full_response = []
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if 'message' in json_response:
                                full_response.append(json_response['message']['content'])
                        except json.JSONDecodeError:
                            continue
                
                result = ''.join(full_response)
                # Save analysis
                self.save_analysis('screenshot', model_name, 'image', result)
                return result
            else:
                error_msg = f"Error: Failed to get response from Ollama. Status code: {response.status_code}"
                if response.text:
                    error_msg += f"\nResponse: {response.text}"
                return error_msg
                
        except Exception as e:
            return f"Error: {str(e)}"

    def create_interface(self):
        """Create Gradio interface"""
        # Get installed models from Ollama
        available_models = self.get_installed_models()
        
        with gr.Blocks(title="Command Line & Screenshot Analysis Tool") as interface:
            gr.Markdown("# Command Line & Screenshot Analysis Tool")
            
            with gr.Tab("Command History Analysis"):
                gr.Markdown("""### Session Format
Each command line session should be wrapped with the following markers:
```
###--- SESSION START ---###
[your commands here]
###--- SESSION END ---###
```
Note: Each marker must have exactly 3 '#' and 3 '-' characters.""")
                
                with gr.Row():
                    cmd_model = gr.Dropdown(
                        choices=available_models,
                        label="Select Model",
                        value=available_models[0] if available_models else None
                    )
                    clear_cmd_btn = gr.Button("Clear")
                    export_btn = gr.Button("Export Analysis History")
                
                with gr.Row():
                    file_upload = gr.File(
                        label="Upload Text File (Optional)",
                        file_types=[".txt"],
                        type="binary"
                    )
                
                with gr.Row():
                    cmd_input = gr.Textbox(
                        label="Command History", 
                        lines=10, 
                        placeholder="Paste command history here or upload a file above..."
                    )
                    cmd_output = gr.Textbox(label="Analysis Result", lines=10, interactive=False)
                
                progress_bar = gr.Progress()
                analyze_cmd_btn = gr.Button("Analyze Commands")
            
            with gr.Tab("Screenshot Analysis"):
                with gr.Row():
                    img_model = gr.Dropdown(
                        choices=[m for m in available_models if any(v in m.lower() for v in ['llava', 'vision'])],
                        label="Select Vision Model"
                    )
                    clear_img_btn = gr.Button("Clear")
                
                with gr.Row():
                    img_input = gr.Image(label="Upload Screenshot", type="filepath")
                    img_output = gr.Textbox(label="Analysis Result", lines=10, interactive=False)
                
                analyze_img_btn = gr.Button("Analyze Screenshot")
            
            # Event handlers
            def process_input(model, text_input, file_input):
                if file_input is not None:
                    return self.analyze_command_history(model, file_input)
                return self.analyze_command_history(model, text_input)
            
            def clear_inputs():
                return "", "", None
            
            def clear_image():
                return None, ""
            
            def export_history():
                return self.history_file
            
            analyze_cmd_btn.click(
                fn=process_input,
                inputs=[cmd_model, cmd_input, file_upload],
                outputs=cmd_output
            )
            
            clear_cmd_btn.click(
                fn=clear_inputs,
                inputs=[],
                outputs=[cmd_input, cmd_output, file_upload]
            )
            
            analyze_img_btn.click(
                fn=self.analyze_screenshot,
                inputs=[img_model, img_input],
                outputs=img_output
            )
            
            clear_img_btn.click(
                fn=clear_image,
                inputs=[],
                outputs=[img_input, img_output]
            )
            
            export_btn.click(
                fn=export_history,
                inputs=[],
                outputs=gr.File(label="Download Analysis History")
            )
        
        return interface

if __name__ == "__main__":
    tool = AnalysisTool()
    interface = tool.create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=True)