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
        self.downloaded_file_info = {}
        
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
        self.downloaded_file_info = {}
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
                    
                    # Clean up the post title to make it filename-friendly
                    def sanitize_filename(title):
                        # Remove or replace characters that are not allowed in filenames
                        return re.sub(r'[<>:"/\\|?*]', '', title).replace(' ', '_')[:50]
                    
                    # Get the post title, use a default if empty
                    post_title = post.title if post.title else f"Instagram_Post_{shortcode}"
                    sanitized_title = sanitize_filename(post_title)
                    
                    # Download the post with a custom filename pattern
                    # This will create files like 2025-02-08_14-00-59_UTC_PostTitle.mp4
                    self.L.download_post(post, target=f"{shortcode}_{sanitized_title}")
                    
                    # Find the downloaded video file
                    file_found = False
                    for file in os.listdir(self.output_dir):
                        if file.endswith('.mp4'):
                            filepath = os.path.join(self.output_dir, file)
                            if any(marker in file for marker in ['_UTC', shortcode]):
                                self.downloaded_files.append(filepath)
                                
                                # Store additional information about the file
                                self.downloaded_file_info[filepath] = {
                                    'title': post_title,
                                    'shortcode': shortcode
                                }
                                
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

                # Try to get the post title from our stored file info
                post_title = self.downloaded_file_info.get(video_path, {}).get('title', 'Unknown_Post')
                
                # Sanitize the title for filename
                def sanitize_filename(title):
                    return re.sub(r'[<>:"/\\|?*]', '', title).replace(' ', '_')[:50]
                sanitized_title = sanitize_filename(post_title)

                base_name = f"{Path(video_path).stem}_{sanitized_title}"
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
            
            # Find the matching transcript filename to get the post title
            matching_transcript = None
            for file in os.listdir(self.output_dir):
                if file.endswith('_transcript.txt'):
                    with open(os.path.join(self.output_dir, file), 'r', encoding='utf-8') as f:
                        if f.read().strip() == transcript.strip():
                            matching_transcript = file
                            break
            
            # Extract the base name and sanitize
            def sanitize_filename(title):
                return re.sub(r'[<>:"/\\|?*]', '', title).replace(' ', '_')[:50]
            
            # Use the base name from the transcript filename, or use a default
            base_name = matching_transcript.replace('_transcript.txt', '') if matching_transcript else 'Unknown_Post'
            
            # Create summary filename
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
        self.downloaded_file_info = {}
        logger.info("Cleared application state")
        return "", "", "", []
    
def create_ui() -> gr.Blocks:
    """Create the Gradio interface"""
    processor = InstagramProcessor()
    
    # Get available models from Ollama
    available_models = get_available_models()
    logger.info(f"Available Ollama models: {available_models}")
    
    def get_latest_transcript():
        """Find the most recently created transcript file"""
        transcript_files = [f for f in os.listdir(processor.output_dir) if f.endswith('_transcript.txt')]
        if not transcript_files:
            return None, None
        
        # Get the most recently created transcript file
        latest_transcript = max(
            [os.path.join(processor.output_dir, f) for f in transcript_files],
            key=os.path.getctime
        )
        return latest_transcript, os.path.basename(latest_transcript)

    def get_latest_summary():
        """Find the most recently created summary file"""
        summary_files = [f for f in os.listdir(processor.output_dir) if f.endswith('_summary.txt')]
        if not summary_files:
            return None, None
        
        # Get the most recently created summary file
        latest_summary = max(
            [os.path.join(processor.output_dir, f) for f in summary_files],
            key=os.path.getctime
        )
        return latest_summary, os.path.basename(latest_summary)

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
                
                # Download buttons for transcript and summary
                with gr.Row():
                    transcript_download = gr.File(
                        label="Download Transcript",
                        interactive=False
                    )
                    summary_download = gr.File(
                        label="Download Summary",
                        interactive=False
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
                outputs=[transcript_output, transcript_download]
            )
            
            def update_transcript_download():
                """Prepare the latest transcript for download"""
                latest_transcript, filename = get_latest_transcript()
                if latest_transcript:
                    return gr.File(value=latest_transcript, visible=True)
                return gr.File(value=None, visible=False)
            
            summarize_btn.click(
                fn=processor.summarize_transcript,
                inputs=[transcript_output, model_dropdown],
                outputs=[summary_output, summary_download]
            )
            
            def update_summary_download():
                """Prepare the latest summary for download"""
                latest_summary, filename = get_latest_summary()
                if latest_summary:
                    return gr.File(value=latest_summary, visible=True)
                return gr.File(value=None, visible=False)
            
            clear_btn.click(
                fn=processor.clear_state,
                inputs=[],
                outputs=[
                    urls,
                    transcript_output,
                    summary_output,
                    downloaded_files,
                    transcript_download,
                    summary_download
                ]
            )
        
        return app

if __name__ == "__main__":
    # Create and launch the app
    app = create_ui()
    app.launch(share=True)