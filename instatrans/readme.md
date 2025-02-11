# Instagram Video Processor

## Overview
This application allows you to download Instagram videos, transcribe their audio, and generate summaries using AI models. It provides a user-friendly Gradio interface for processing Instagram content.

## Repository
- **Code Repository**: [https://github.com/lafintiger/FunWithLLMs](https://github.com/lafintiger/FunWithLLMs)

## Prerequisites

### Software Requirements
- Python 3.8+
- Ollama (for AI model inference)
- Faster-Whisper-XXL
- Instaloader

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lafintiger/FunWithLLMs.git
   cd FunWithLLMs
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
   - Download from: [Whisper Standalone Win](https://github.com/Purfview/whisper-standalone-win)
   - Extract the executable to a known directory (e.g., `D:\CodeRepo\Faster-Whisper-XXL`)
   - Update the path in the Gradio interface when running the application

6. **Install Instaloader**
   ```bash
   pip install instaloader
   ```

[... rest of the README remains the same ...]# Instagram Video Processor

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
   git clone https://github.com/yourusername/instagram-video-processor.git
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
   - Download the executable from: [Insert Link to Faster-Whisper-XXL Release]
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
   python test6.py
   ```

2. In the Gradio interface:
   - Enter Instagram Video URLs
   - (Optional) Provide Instagram login credentials
   - Click "Download Videos"
   - Select an AI model for summarization
   - Transcribe and generate summaries

### Processing Workflow

#### Downloading Videos
- Enter Instagram video URLs in the input box
- Click "Download Videos"
- Videos will be saved in the `downloads` directory

#### Transcribing Videos
- After downloading, click "Transcribe Videos"
- Transcripts are automatically generated
- Use the "Download Transcript" button to save the transcript file

#### Generating Summaries
- Select an AI model from the dropdown
- Click "Generate Summary"
- Use the "Download Summary" button to save the summary file

### File Management
- All files are saved in the `downloads` directory
- Filename format: 
  - Videos: `{timestamp}_{video_title}.mp4`
  - Transcripts: `{timestamp}_{video_title}_transcript.txt`
  - Summaries: `{timestamp}_{video_title}_summary.txt`

### Download Features
- Convenient built-in download buttons for transcripts and summaries
- Always downloads the most recently generated file
- No need to manually browse file system

## Features
- Download Instagram videos (public and private)
- One-click transcription using Faster-Whisper-XXL
- AI-powered summaries with Ollama models
- Easy file downloads directly in the interface
- Organized file naming with video titles

## Troubleshooting

### Common Issues
- **Model Not Found**: Ensure Ollama is running and models are pulled
- **Download Failed**: Check URL, account permissions
- **Transcription Error**: Verify Faster-Whisper-XXL path
- **Login Issues**: Use app-specific password or temporary account

### Troubleshooting Download Issues
- Check internet connection
- Verify Instagram URL
- Ensure you have necessary permissions
- Check Ollama and Whisper configurations

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
- This tool is for educational and research purposes
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
   git clone https://github.com/yourusername/instagram-video-processor.git
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
   - Download the executable from: [Insert Link to Faster-Whisper-XXL Release]
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
   python test6.py
   ```

2. In the Gradio interface:
   - Enter Instagram Video URLs
   - (Optional) Provide Instagram login credentials
   - Click "Download Videos"
   - Select an AI model for summarization
   - Transcribe and generate summaries

### Downloading Transcripts and Summaries

#### Transcript Location
- Transcripts are automatically saved in the `downloads` directory
- Filename format: `{timestamp}_{video_title}_transcript.txt`
- To download:
  1. Navigate to the `downloads` folder in your project directory
  2. Locate the transcript file
  3. Open or copy the file as needed

#### Summary Location
- Summaries are saved alongside transcripts in the `downloads` directory
- Filename format: `{timestamp}_{video_title}_summary.txt`
- To download:
  1. Navigate to the `downloads` folder in your project directory
  2. Locate the summary file
  3. Open or copy the file as needed

**Tip**: The Gradio interface displays the full file path for each generated transcript and summary, making it easy to locate the files.

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