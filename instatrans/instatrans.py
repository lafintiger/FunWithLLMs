import gradio as gr
import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_community.llms import Ollama
import logging
import requests
import instaloader
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434"
OUTPUT_DIR = os.path.join(os.getcwd(), "downloads")

def get_available_models():
    """Fetch available models from Ollama"""
    try:
        logger.info("Attempting to fetch models from Ollama...")
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            model_names = [model['name'] for model in models]
            logger.info(f"Found models: {model_names}")
            return model_names
        else:
            logger.error(f"Error status code: {response.status_code}")
            return ["llama2"]
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return ["llama2"]

class InstagramProcessor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InstagramProcessor, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        # Set up output directory
        self.output_dir = OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize downloaded files list
        self.downloaded_files = []
        
        # Set up instaloader
        self.L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=self.output_dir
        )
        
        logger.info(f"Initialized InstagramProcessor with output directory: {self.output_dir}")
        self.initialized = True
        
    def setup_ollama(self, model_name: str) -> Ollama:
        """Initialize Ollama with specified model"""
        logger.info("Setting up Ollama with model: %s", model_name)
        return Ollama(model=model_name)

    def extract_shortcode_from_url(self, url: str) -> str:
        """Extract the shortcode from an Instagram URL"""
        patterns = [
            r'instagram.com/p/([^/?]+)',
            r'instagram.com/reel/([^/?]+)',
            r'instagram.com/tv/([^/?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def download_videos(
        self, 
        urls: str, 
        username: Optional[str] = None, 
        password: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """Download videos from Instagram using instaloader"""
        if not urls.strip():
            return "Please provide at least one URL", []

        self.downloaded_files = []
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        logger.info("Processing %d URLs", len(url_list))
        
        try:
            if username and password:
                try:
                    self.L.login(username, password)
                    logger.info("Successfully logged in to Instagram")
                except Exception as e:
                    logger.error(f"Login failed: {str(e)}")
                    return f"Login failed: {str(e)}", []

            for url in url_list:
                try:
                    shortcode = self.extract_shortcode_from_url(url)
                    if not shortcode:
                        logger.error(f"Could not extract shortcode from URL: {url}")
                        continue

                    post = instaloader.Post.from_shortcode(self.L.context, shortcode)
                    
                    # Download the post
                    self.L.download_post(post, target=shortcode)
                    
                    # Find the downloaded video file
                    file_found = False
                    for file in os.listdir(self.output_dir):
                        if file.endswith('.mp4'):
                            filepath = os.path.join(self.output_dir, file)
                            if any(marker in file for marker in ['_UTC', shortcode]):
                                self.downloaded_files.append(filepath)
                                logger.info(f"Successfully found video file: {filepath}")
                                file_found = True
                                break
                    
                    if not file_found:
                        logger.warning(f"Could not find downloaded file for shortcode: {shortcode}")
                    
                except Exception as e:
                    logger.error(f"Error downloading {url}: {str(e)}")
                    continue

            if self.downloaded_files:
                success_msg = "Successfully downloaded/found videos:\n"
                for file in self.downloaded_files:
                    success_msg += f"- {file}\n"
                return success_msg, self.downloaded_files
            else:
                error_msg = "No videos were downloaded. If the video exists in the downloads folder, it might not have been detected properly."
                logger.warning(error_msg)
                return error_msg, []
            
        except Exception as e:
            error_msg = f"Error during download process: {str(e)}"
            logger.error(error_msg)
            return error_msg, []

    def transcribe_videos(
        self, 
        whisper_path: str,
        downloaded_files: List[str]
    ) -> str:
        """Transcribe videos using Faster-Whisper-XXL"""
        if not downloaded_files:
            return "No videos to transcribe"

        all_transcripts = []
        logger.info(f"Starting transcription for {len(downloaded_files)} files")
        
        try:
            for video_path in downloaded_files:
                if not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    continue

                base_name = Path(video_path).stem
                logger.info(f"Processing video: {base_name}")

                # Create temporary directory
                temp_dir = os.path.join(self.output_dir, f"temp_{base_name}")
                os.makedirs(temp_dir, exist_ok=True)
                logger.info(f"Created temp directory: {temp_dir}")

                # Set up output paths
                output_transcript = os.path.join(self.output_dir, f"{base_name}_transcript.txt")
                
                # Construct whisper command
                exe_path = os.path.join(whisper_path, "faster-whisper-xxl.exe")
                cmd_str = f'"{exe_path}" "{video_path}" --language English --model medium --output_dir "{temp_dir}"'
                logger.info(f"Executing command: {cmd_str}")

                try:
                    # Run transcription
                    result = subprocess.run(
                        cmd_str,
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    
                    # Log the complete output for debugging
                    logger.info(f"Command stdout: {result.stdout}")
                    logger.error(f"Command stderr: {result.stderr}")

                    if result.returncode != 0:
                        error_msg = f"Transcription command failed:\n{result.stderr}"
                        logger.error(error_msg)
                        all_transcripts.append(f"Error transcribing {base_name}: {error_msg}")
                        continue

                    # Find and read transcript files
                    transcript_content = []
                    if os.path.exists(temp_dir):
                        for file in os.listdir(temp_dir):
                            if file.endswith(('.txt', '.srt', '.vtt')):
                                file_path = os.path.join(temp_dir, file)
                                logger.info(f"Reading transcript file: {file_path}")
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read().strip()
                                        if content:
                                            transcript_content.append(content)
                                except Exception as e:
                                    logger.error(f"Error reading transcript file {file_path}: {e}")

                    # Combine and save transcripts
                    if transcript_content:
                        combined_transcript = "\n\n".join(transcript_content)
                        
                        # Save to final location
                        try:
                            with open(output_transcript, 'w', encoding='utf-8') as f:
                                f.write(combined_transcript)
                            logger.info(f"Saved transcript to: {output_transcript}")
                            all_transcripts.append(f"Transcript for {base_name}:\n{combined_transcript}")
                        except Exception as e:
                            logger.error(f"Error saving transcript to {output_transcript}: {e}")
                            all_transcripts.append(f"Error saving transcript for {base_name}: {str(e)}")
                    else:
                        error_msg = f"No transcript content found for {base_name}"
                        logger.error(error_msg)
                        all_transcripts.append(error_msg)

                except Exception as e:
                    logger.error(f"Error processing {base_name}: {str(e)}")
                    all_transcripts.append(f"Error processing {base_name}: {str(e)}")

                finally:
                    # Clean up temp directory
                    try:
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        logger.info(f"Cleaned up temp directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Could not clean up temp directory {temp_dir}: {e}")

            if not all_transcripts:
                return "No transcripts were generated successfully."
                
            return "\n\n---\n\n".join(all_transcripts)
            
        except Exception as e:
            error_msg = f"Unexpected error during transcription: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # ... rest of the code remains the same
        
        def transcribe_videos(
        self, 
        whisper_path: str,
        downloaded_files: List[str]
    ) -> str:
         """Transcribe videos using Faster-Whisper-XXL"""
        if not downloaded_files:
            return "No videos to transcribe"

        all_transcripts = []
        logger.info(f"Starting transcription for {len(downloaded_files)} files")
        
        try:
            for video_path in downloaded_files:
                if not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    continue

                base_name = Path(video_path).stem
                logger.info(f"Processing video: {base_name}")

                # Create temporary directory
                temp_dir = os.path.join(self.output_dir, f"temp_{base_name}")
                os.makedirs(temp_dir, exist_ok=True)
                logger.info(f"Created temp directory: {temp_dir}")

                # Set up output paths
                output_transcript = os.path.join(self.output_dir, f"{base_name}_transcript.txt")
                
                # Construct whisper command
                exe_path = os.path.join(whisper_path, "faster-whisper-xxl.exe")
                cmd_str = f'"{exe_path}" "{video_path}" --language English --model medium --output_dir "{temp_dir}"'
                logger.info(f"Executing command: {cmd_str}")

                try:
                    # Run transcription
                    result = subprocess.run(
                        cmd_str,
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    
                    # Log the complete output for debugging
                    logger.info(f"Command stdout: {result.stdout}")
                    logger.error(f"Command stderr: {result.stderr}")

                    if result.returncode != 0:
                        error_msg = f"Transcription command failed:\n{result.stderr}"
                        logger.error(error_msg)
                        all_transcripts.append(f"Error transcribing {base_name}: {error_msg}")
                        continue

                    # Find and read transcript files
                    transcript_content = []
                    if os.path.exists(temp_dir):
                        for file in os.listdir(temp_dir):
                            if file.endswith(('.txt', '.srt', '.vtt')):
                                file_path = os.path.join(temp_dir, file)
                                logger.info(f"Reading transcript file: {file_path}")
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read().strip()
                                        if content:
                                            transcript_content.append(content)
                                except Exception as e:
                                    logger.error(f"Error reading transcript file {file_path}: {e}")

                    # Combine and save transcripts
                    if transcript_content:
                        combined_transcript = "\n\n".join(transcript_content)
                        
                        # Save to final location
                        try:
                            with open(output_transcript, 'w', encoding='utf-8') as f:
                                f.write(combined_transcript)
                            logger.info(f"Saved transcript to: {output_transcript}")
                            all_transcripts.append(f"Transcript for {base_name}:\n{combined_transcript}")
                        except Exception as e:
                            logger.error(f"Error saving transcript to {output_transcript}: {e}")
                            all_transcripts.append(f"Error saving transcript for {base_name}: {str(e)}")
                    else:
                        error_msg = f"No transcript content found for {base_name}"
                        logger.error(error_msg)
                        all_transcripts.append(error_msg)

                except Exception as e:
                    logger.error(f"Error processing {base_name}: {str(e)}")
                    all_transcripts.append(f"Error processing {base_name}: {str(e)}")

                finally:
                    # Clean up temp directory
                    try:
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        logger.info(f"Cleaned up temp directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Could not clean up temp directory {temp_dir}: {e}")

            if not all_transcripts:
                return "No transcripts were generated successfully."
                
            return "\n\n---\n\n".join(all_transcripts)
            
        except Exception as e:
            error_msg = f"Unexpected error during transcription: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def summarize_transcript(
        self, 
        transcript: str, 
        model_name: str
    ) -> str:
        """Summarize transcript using Ollama"""
        if not transcript.strip():
            return "No transcript to summarize"

        try:
            logger.info("Starting summarization with model: %s", model_name)
            llm = self.setup_ollama(model_name)
            
            prompt = f"""Please provide a concise summary of the following transcript:

{transcript}

Focus on the main points and key takeaways."""

            # Use invoke() instead of direct call
            response = llm.invoke(prompt)
            logger.info("Successfully generated summary")
            
            # Find the transcript filename to match the summary name
            for file in os.listdir(self.output_dir):
                if file.endswith('_transcript.txt'):
                    base_name = file.replace('_transcript.txt', '')
                    summary_filename = f"{base_name}_summary.txt"
                    summary_path = os.path.join(self.output_dir, summary_filename)
                    
                    # Save the summary
                    try:
                        with open(summary_path, 'w', encoding='utf-8') as f:
                            f.write(f"Original Transcript:\n\n{transcript}\n\n")
                            f.write(f"Summary (Generated by {model_name}):\n\n{response}")
                        
                        logger.info(f"Summary saved to: {summary_path}")
                        
                        # Add file location to the response
                        full_response = f"Summary (saved to {summary_path}):\n\n{response}"
                        return full_response
                    except Exception as e:
                        logger.error(f"Failed to save summary file: {e}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error("Summary generation error: %s", str(e))
            return error_msg

    def clear_state(self) -> Tuple[str, str, str, List[str]]:
        """Clear the application state"""
        self.downloaded_files = []
        logger.info("Cleared application state")
        return "", "", "", []
    
def create_ui() -> gr.Blocks:
    """Create the Gradio interface"""
    processor = InstagramProcessor()
    
    # Get available models from Ollama
    available_models = get_available_models()
    logger.info(f"Available Ollama models: {available_models}")
    
    with gr.Blocks(title="Instagram Video Processor") as app:
        gr.Markdown("# Instagram Video Processor")
        
        with gr.Tab("Configuration"):
            whisper_path = gr.Textbox(
                label="Path to Faster-Whisper-XXL executable",
                placeholder="Enter the full path to the whisper executable",
                value="D:\\CodeRepo\\Faster-Whisper-XXL",
                info="Default path can be changed if needed"
            )
        
        with gr.Tab("Process Videos"):
            # Input section
            with gr.Group():
                gr.Markdown("### Input URLs and Credentials")
                urls = gr.Textbox(
                    label="Instagram Video URLs",
                    placeholder="Enter one URL per line",
                    lines=5
                )
                with gr.Row():
                    username = gr.Textbox(
                        label="Instagram Username (optional)",
                        placeholder="Enter your username"
                    )
                    password = gr.Textbox(
                        label="Instagram Password (optional)",
                        placeholder="Enter your password",
                        type="password"
                    )
        
            # Processing section
            with gr.Group():
                gr.Markdown("### Processing Controls")
                with gr.Row():
                    download_btn = gr.Button("Download Videos", variant="primary")
                    transcribe_btn = gr.Button("Transcribe Videos", variant="primary")
                    clear_btn = gr.Button("Clear All", variant="secondary")
                
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=available_models,
                        value=available_models[0] if available_models else None,
                        label="Select AI Model for Summary",
                        interactive=True,
                        container=True
                    )
                    summarize_btn = gr.Button("Generate Summary", variant="primary")
            
            # Output section
            with gr.Group():
                gr.Markdown("### Results")
                download_output = gr.Textbox(
                    label="Download Status",
                    interactive=False,
                    lines=5
                )
                downloaded_files = gr.State([])
                transcript_output = gr.Textbox(
                    label="Transcription",
                    interactive=False,
                    lines=10
                )
                summary_output = gr.Textbox(
                    label="Summary",
                    interactive=False,
                    lines=5
                )
            
            # Event handlers
            download_btn.click(
                fn=processor.download_videos,
                inputs=[urls, username, password],
                outputs=[download_output, downloaded_files]
            )
            
            transcribe_btn.click(
                fn=processor.transcribe_videos,
                inputs=[whisper_path, downloaded_files],
                outputs=transcript_output
            )
            
            summarize_btn.click(
                fn=processor.summarize_transcript,
                inputs=[transcript_output, model_dropdown],
                outputs=summary_output
            )
            
            clear_btn.click(
                fn=processor.clear_state,
                inputs=[],
                outputs=[
                    urls,
                    transcript_output,
                    summary_output,
                    downloaded_files
                ]
            )
        
        return app

if __name__ == "__main__":
    # Create and launch the app
    app = create_ui()
    app.launch(share=True)
    