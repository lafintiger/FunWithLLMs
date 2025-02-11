# Instagram Video Processor

## Overview
This application allows you to download Instagram videos, transcribe their audio, and generate summaries using AI models. It provides a user-friendly Gradio interface for processing Instagram content.

## Prerequisites

### Software Requirements
- Python 3.8+
- Ollama (for AI model inference)
- Faster-Whisper-XXL
- Instaloader

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lafintiger/instagram-video-processor.git
   cd instagram-video-processor
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**
   - Download and install from: https://ollama.com/
   - Pull at least one model (recommended: mistral or llama3)
   ```bash
   ollama pull mistral
   ```

5. **Install Faster-Whisper-XXL**
   - Download the executable (https://github.com/Purfview/whisper-standalone-win)
   - Place the executable in a known directory (e.g., `D:\CodeRepo\Faster-Whisper-XXL`)
   - Update the path in the Gradio interface when running the application

6. **Install Instaloader**
   ```bash
   pip install instaloader
   ```

## Configuration

### Ollama Setup
- Ensure Ollama is running locally (typically at http://localhost:11434)
- The application will automatically detect available models

### Instagram Credentials
- Optional: Provide Instagram username/password for private content
- Recommended: Use a separate Instagram account for downloading

## Usage

1. Run the application:
   ```bash
   python instatrans.py
   ```

2. In the Gradio interface:
   - Enter Instagram Video URLs
   - (Optional) Provide Instagram login credentials
   - Click "Download Videos"
   - Select an AI model for summarization
   - Transcribe and generate summaries

## Features
- Download Instagram videos (public and private)
- Transcribe video audio using Faster-Whisper-XXL
- Generate AI summaries using Ollama models
- Organized file naming with video titles

## Troubleshooting

### Common Issues
- **Model Not Found**: Ensure Ollama is running and models are pulled
- **Download Failed**: Check URL, account permissions
- **Transcription Error**: Verify Faster-Whisper-XXL path
- **Login Issues**: Use app-specific password or temporary account

### Logging
- Detailed logs are printed to console
- Check log messages for specific error details

## Dependencies
See `requirements.txt` for full list of Python package dependencies

## License
[Insert Your License Here]

## Contributing
Contributions are welcome! Please submit pull requests or open issues.

## Disclaimer
- Respect Instagram's Terms of Service
- Use responsibly and ethically
- Obtain necessary permissions for content usage