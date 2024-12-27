# Command Line & Screenshot Analysis Tool

A Gradio-based web interface for analyzing command line histories and screenshots using local LLM models via Ollama. This tool provides intelligent analysis of command line sessions and visual content using your choice of locally installed AI models.

## Features

- **Command Line Analysis**
  - Analyze single or multiple command line sessions
  - Batch processing support
  - File upload capability
  - Progress tracking for batch operations
  - Session-based analysis with clear separation

- **Screenshot Analysis**
  - Support for image analysis using vision-capable models
  - Compatible with models like LLaVA and Llama-2-vision

- **General Features**
  - Local model selection via Ollama
  - Export functionality for analysis history
  - Progress tracking
  - Automatic history saving
  - Public link sharing option

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Sufficient system resources to run local LLM models

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/command-line-analysis-tool.git
cd command-line-analysis-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running:
- Visit [Ollama's website](https://ollama.ai/download) for installation instructions
- Start the Ollama service
- Pull your desired models (e.g., `ollama pull llama2`)

## Usage

1. Start the application:
```bash
python evaluator.py
```

2. Access the interface:
- Local: http://localhost:7860
- Public: Check console output for public URL

3. Select a model from the dropdown menu

4. For command line analysis:
   - Paste command history directly or
   - Upload a text file with command sessions
   - Use session markers for batch processing:
```
###--- SESSION START ---###
[your commands here]
###--- SESSION END ---###
```

5. For screenshot analysis:
   - Select a vision-capable model
   - Upload your screenshot
   - View the analysis results

## File Format for Batch Processing

When analyzing multiple command line sessions, use the following format:

```text
###--- SESSION START ---###
cd /etc
ls -la
vim hosts
###--- SESSION END ---###

###--- SESSION START ---###
yum install nginx
systemctl start nginx
###--- SESSION END ---###
```

## Export and History

- Analysis results are automatically saved with timestamps
- Use the "Export Analysis History" button to download results
- History is saved in CSV format for easy processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

## Support

For issues and feature requests, please use the GitHub issues page.