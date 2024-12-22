# Prompt Hacking Testing Interface - User Manual

## Overview

The Prompt Hacking Testing Interface is a powerful tool designed to analyze how different language models respond to varied prompt formulations. This application allows researchers and developers to systematically test model responses by generating prompt variations and evaluating their effectiveness.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Ollama installed and running locally
- Required Python libraries:
  - gradio
  - requests
  - pandas
  - dataclasses (for Python 3.7+)

### Setup Instructions
1. Ensure Ollama is running on localhost:11434
2. Install required dependencies:
   ```
   pip install gradio requests pandas
   ```
3. Save the script as `prompt-hacking-5.py`
4. Run the script:
   ```
   python prompt-hacking-5.py
   ```

## Interface Components

### Model Selection
- **Test Model Dropdown**: Select the language model to be tested
- **Evaluator Model Dropdown**: Choose the model that will assess the test model's responses
- Both dropdowns are populated dynamically from available Ollama models

### Test Configuration
- **Test Category Dropdown**: 
  - Options include:
    - Safety Test
    - Capability Test
    - Jailbreak Test
    - General Test
    - Uncategorized
- **Number of Variations Slider**: 
  - Adjust the number of prompt variations (1-100)
  - Default is 10 variations

### Prompt Input
- Large text box where you enter the original prompt to be tested

## Testing Process

### How Automated Testing Works
1. Enter your prompt in the input box
2. Select test and evaluator models
3. Choose a test category
4. Set the number of prompt variations
5. Click "Start Automated Testing"

### Prompt Variation Generation
- The tool uses a "l33t speak" transformation algorithm
- Replaces characters with similar-looking alternatives
- Generates multiple variations of the original prompt
- Helps test model robustness to different input styles

### Evaluation Process
- Each prompt (original and variations) is:
  1. Sent to the test model
  2. The response is evaluated by the evaluator model
  3. Assessed strictly on whether the EXACT request was fulfilled

## Output Sections

### Variations List
- Shows the original prompt and all generated variations

### Current Prompt
- Displays the specific prompt currently being tested

### Test Model Response
- Shows the response from the selected test model

### Evaluator Model Assessment
- Provides an objective evaluation of the response
- Indicates 'YES' or 'NO' based on exact request fulfillment

### Response Time
- Displays the time taken to generate the response

### Test Summary
- Total number of tests conducted
- Success rates by:
  - Individual models
  - Test categories
- Detailed performance breakdown

## Result Tracking

### CSV Export
- After each test session, results are automatically exported
- Filename format: `test_results_YYYYMMDD_HHMMSS.csv`
- Includes detailed information about each test

### Successful Prompts Log
- Prompts that successfully bypass model restrictions are logged
- Saved in `successful_prompts.txt`

## Ethical Considerations
- This tool is intended for research and security testing
- Use responsibly and in compliance with ethical guidelines
- Do not use for malicious purposes

## Troubleshooting
- Ensure Ollama is running before launching the interface
- Check that models are available in the Ollama local instance
- Verify Python and library dependencies are correctly installed

## Limitations
- Requires local Ollama setup
- Evaluation is based on a predefined, strict matching criteria
- Results may vary between different model versions

## Tips for Effective Testing
1. Start with a diverse set of prompts
2. Use various test categories
3. Compare multiple models
4. Pay attention to the success rates and patterns

## Contributing
Interested in improving the tool? Consider:
- Enhancing variation generation algorithms
- Adding more sophisticated evaluation criteria
- Implementing additional export and analysis features

## License and Attribution

### Apache License 2.0

This project is licensed under the Apache License, Version 2.0 (the "License"). 

#### Key Terms
- You may use, modify, and distribute the software
- You must give appropriate credit
- Modifications must be clearly marked
- No warranty is provided

#### Full License
For the complete license text, please see the `LICENSE` file in the repository or visit:
http://www.apache.org/licenses/LICENSE-2.0

#### Key Obligations
- Include a copy of the license with any distribution
- Retain all copyright, patent, trademark, and attribution notices
- If you modify the source, you must clearly mark your modifications
- Provide attribution to the original creators

#### Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## Contributing and Support

### Reporting Issues
- Use the GitHub Issues section for:
  - Bug reports
  - Feature requests
  - Performance improvements
  - Security vulnerabilities

#### How to File an Issue
1. Go to the GitHub repository
2. Click on the "Issues" tab
3. Click "New Issue"
4. Choose an appropriate issue template
5. Provide a clear, detailed description
6. Include:
   - Steps to reproduce the issue
   - Expected vs. actual behavior
   - Your environment details (OS, Python version, Ollama version)

### Contributing Guidelines
1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request
5. Ensure all tests pass
6. Provide a clear description of your changes

### Community Support
- Check existing issues before creating a new one
- Be respectful and constructive
- Follow the project's code of conduct
- Help other community members when possible

### Disclaimer
This tool is for research and ethical testing purposes only. Users are responsible for responsible and legal use.
