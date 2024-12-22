# Prompt Hacking Testing Interface

## Overview

The Prompt Hacking Testing Interface is an open-source tool designed to automate the testing of local Large Language Models (LLMs) for vulnerability assessment and security research.

## Academic Background

This tool is inspired by the research paper:
- **Title**: "Best-of-N Jailbreaking"
- **Category**: Computer Science > Computation and Language
- **Submitted**: 4 December 2024
- **arXiv**: [https://arxiv.org/abs/2412.03556](https://arxiv.org/abs/2412.03556)

**Note**: This implementation is based on the academic research, adapted for local model testing and security analysis.

## Purpose

This tool enables researchers, developers, and AI safety experts to:
- Systematically test LLM responses to various prompt variations
- Evaluate model susceptibility to different input strategies
- Conduct comprehensive security and capability assessments

## Key Features

- 🖥️ Intuitive Gradio Interface
- 🔍 Automated Prompt Variation Generation
- 🔬 Comprehensive Model Testing
- 💾 Detailed Result Tracking and Export
- 🔒 Local, Secure Testing Environment

## Prerequisites

### System Requirements
- Python 3.8+
- Ollama running on default port (11434)
- Pre-downloaded models for testing

### Dependencies
- gradio
- requests
- pandas
- dataclasses

## Installation

1. Ensure Ollama is running
2. Install required dependencies:
   ```bash
   pip install gradio requests pandas
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/lafintiger/FunWithLLMs.git
   cd FunWithLLMs
   ```
4. Run the application:
   ```bash
   python best-of-n.py
   ```

## Usage

1. Select test and evaluator models from dropdown
2. Choose a test category
3. Enter your prompt
4. Adjust variation count
5. Start automated testing
6. Review results and exported CSV

## Advantages

- 🆓 Completely Free
- 🔒 Secure Local Testing
- 🚫 No External API Costs
- 🛡️ Confidential Results

## Ethical Considerations

This tool is intended for:
- Research purposes
- Responsible AI safety testing
- Academic and professional security assessments

**WARNING**: Use responsibly and ethically. Do not use for malicious purposes.

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details on how to get started.

## License

Apache License 2.0 - See `LICENSE` file for details.

## Acknowledgments

Special thanks to:
- Original research paper authors
- Qwen Coder 2.5
- Claude Sonnet
- Claude Haiku

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. USE AT YOUR OWN RISK.
