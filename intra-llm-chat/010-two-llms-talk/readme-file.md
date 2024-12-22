# FunWithLLMs: Two LLMs Talking

## Overview

FunWithLLMs is a Flask-based web application that enables interactive conversations between two different Large Language Models (LLMs) using Ollama. This unique tool allows you to:
- Dynamically fetch available Ollama models
- Select two models to engage in a conversation
- Assign custom personalities to each model
- Configure personality traits with granular sliders
- Observe AI-generated dialogues in real-time

## Key Features

- Dynamic model selection from available Ollama models
- Customizable personality configuration
  - Free-form personality description
  - Five-trait personality slider (Big Five model):
    1. Openness
    2. Conscientiousness
    3. Extraversion
    4. Agreeableness
    5. Neuroticism
- Real-time conversation generation
- Interactive web interface
- Conversation start/stop controls

## Prerequisites

- Python 3.7+
- Ollama installed and running locally
- Flask
- Requests library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lafintiger/FunWithLLMs.git
cd FunWithLLMs/two-llms-talk
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install flask requests
```

4. Ensure Ollama is running on localhost:11434
   - Install Ollama from: https://ollama.com/
   - Pull desired models using: `ollama pull <model-name>`

## Running the Application

```bash
python app.py
```

Open a web browser and navigate to `http://localhost:5000`

## Technical Details

- Uses Flask for web framework
- Communicates with Ollama API at `http://localhost:11434`
- Supports dynamic model selection
- Allows custom personality prompts for each model
- Implements Big Five personality trait configuration

## License

Apache License 2.0 - See LICENSE file for full details

## Contributing

Contributions are welcome! 
- Fork the repository
- Create your feature branch
- Commit your changes
- Push to the branch
- Create a new Pull Request

## Troubleshooting

- Verify Ollama is running before starting the application
- Confirm models are available via `ollama list`
- Check Python and dependency versions
- Ensure all dependencies are installed

## Contact

For issues, questions, or suggestions:
- Open a GitHub issue
- Email: [Your Contact Email]

## Disclaimer

This is an experimental tool. AI-generated conversations may be unpredictable and should be used for entertainment and exploration purposes.# FunWithLLMs: Two LLMs Talking

## Overview

FunWithLLMs is a Flask-based web application that enables interactive conversations between two different Large Language Models (LLMs) using Ollama. This unique tool allows you to:
- Dynamically fetch available Ollama models
- Select two models to engage in a conversation
- Assign custom personalities to each model
- Observe AI-generated dialogues in real-time

## How It Works

The application leverages the Ollama API to:
1. Retrieve available language models
2. Generate responses based on selected models
3. Create conversational interactions with personalized prompts

## Prerequisites

- Python 3.7+
- Ollama installed and running locally
- Flask
- Requests library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lafintiger/FunWithLLMs.git
cd FunWithLLMs/two-llms-talk
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install flask requests
```

4. Ensure Ollama is running on localhost:11434
   - Install Ollama from: https://ollama.com/
   - Pull desired models using: `ollama pull <model-name>`

## Running the Application

```bash
python app.py
```

Open a web browser and navigate to `http://localhost:5000`

## Technical Details

- Uses Flask for web framework
- Communicates with Ollama API at `http://localhost:11434`
- Supports dynamic model selection
- Allows custom personality prompts for each model

## License

Apache License 2.0 - See LICENSE file for full details

## Contributing

Contributions are welcome! 
- Fork the repository
- Create your feature branch
- Commit your changes
- Push to the branch
- Create a new Pull Request

## Troubleshooting

- Verify Ollama is running before starting the application
- Confirm models are available via `ollama list`
- Check Python and dependency versions

## Contact

For issues, questions, or suggestions:
- Open a GitHub issue
- Email: [Your Contact Email]

## Disclaimer

This is an experimental tool. AI-generated conversations may be unpredictable and should be used for entertainment and exploration purposes.# FunWithLLMs: Two LLMs Talking

## Overview

FunWithLLMs is a Flask-based web application that allows you to create conversations between two different Large Language Models (LLMs) using Ollama. This interactive tool lets you select models, assign personalities, and watch them engage in a dialogue.

## Features

- Fetch available Ollama models dynamically
- Select two different models for conversation
- Assign custom personalities to each model
- Initiate and continue conversations between models
- Web interface for easy interaction

## Prerequisites

- Python 3.7+
- Flask
- Requests library
- Ollama installed and running locally

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lafintiger/FunWithLLMs.git
cd FunWithLLMs/two-llms-talk
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install flask requests
```

4. Ensure Ollama is running on localhost:11434

## Running the Application

```bash
python app.py
```

Open a web browser and navigate to `http://localhost:5000`

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

- Ensure Ollama is running before starting the application
- Check that you have models available in Ollama
- Verify all dependencies are installed correctly

## Contact

For issues or questions, please open an issue on the GitHub repository.
