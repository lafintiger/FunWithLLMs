# Command Line & Screenshot Analysis Tool User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Command Line Analysis](#command-line-analysis)
3. [Screenshot Analysis](#screenshot-analysis)
4. [Working with Sessions](#working-with-sessions)
5. [File Management](#file-management)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. Ensure Ollama is installed and running:
   - Download from [ollama.ai](https://ollama.ai/download)
   - Follow installation instructions for your OS
   - Start the Ollama service

2. Install required models:
   ```bash
   ollama pull llama2        # For command analysis
   ollama pull llava         # For screenshot analysis
   ```

3. Start the application:
   ```bash
   python evaluator.py
   ```

### Interface Overview

The interface consists of two main tabs:
- Command History Analysis
- Screenshot Analysis

Each tab has:
- Model selection dropdown
- Input area
- Analysis results display
- Control buttons

## Command Line Analysis

### Single Session Analysis

1. Select a model from the dropdown
2. Paste your command history in the text box
3. Click "Analyze Commands"
4. View results in the output area

### Batch Processing

1. Prepare your sessions using markers:
```text
###--- SESSION START ---###
cd /var/log
tail -f syslog
###--- SESSION END ---###

###--- SESSION START ---###
systemctl status nginx
systemctl restart nginx
###--- SESSION END ---###
```

2. Either:
   - Paste the formatted text directly, or
   - Save as .txt file and use the upload option

3. Click "Analyze Commands"
4. Watch the progress bar
5. View individual session analyses

### File Upload

1. Click "Upload Text File"
2. Select your .txt file
3. Ensure it contains properly formatted sessions
4. Click "Analyze Commands"

## Screenshot Analysis

1. Select a vision-capable model (e.g., llava)
2. Upload your screenshot
3. Click "Analyze Screenshot"
4. View the detailed description and analysis

### Supported Image Types
- PNG
- JPEG
- GIF (first frame only)

## Working with Sessions

### Session Format Rules
- Must start with `###--- SESSION START ---###`
- Must end with `###--- SESSION END ---###`
- Exactly 3 '#' characters
- Exactly 3 '-' characters
- Case sensitive

### Best Practices
- Keep sessions focused on related commands
- Include context when necessary
- Separate different tasks into different sessions
- Include error messages if relevant

## File Management

### History Export
1. Click "Export Analysis History"
2. Save the CSV file
3. Open in spreadsheet software

### CSV Format
The exported file contains:
- Timestamp
- Analysis type (command/screenshot)
- Model used
- Input content
- Analysis results

### File Organization
- Keep related sessions in single files
- Use descriptive filenames
- Back up your analysis history regularly

## Troubleshooting

### Common Issues

1. "Error connecting to Ollama"
   - Check if Ollama is running
   - Verify the port (default: 11434)
   - Restart Ollama service

2. "Model not found"
   - Install the model using `ollama pull [model-name]`
   - Check model name spelling
   - Verify model compatibility

3. "Invalid session markers"
   - Check exact format of markers
   - Verify no extra spaces
   - Ensure proper start/end pairing

### Getting Help

1. Check the console for error messages
2. Verify your Python environment
3. Ensure all dependencies are installed
4. Check GitHub issues for similar problems

### Best Practices

1. Regular Testing
   - Test with small sessions first
   - Verify model responses
   - Monitor system resources

2. Maintenance
   - Keep Ollama updated
   - Update Python packages
   - Back up analysis history
   - Monitor disk space

3. Performance
   - Close unused applications
   - Monitor RAM usage
   - Consider GPU requirements
   - Limit batch sizes appropriately