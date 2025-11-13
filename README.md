# MDMA AI Agent

Conversational AI Agent built with Langgraph and Ollama

## Features
- Interactive chat interface
- Memory-enabled conversations
- Powered by local LLM (Llama3 via Ollama)
- State management with Langgraph

## Prerequisites

### 1. Python 3.8+
Download from: https://www.python.org/

### 2. Ollama
Download and install from: https://ollama.ai

After installation, pull the Llama3 model:
```bash
ollama pull llama3
```

## Installation

### Method 1: Clone from GitHub (if available)
```bash
git clone [YOUR_REPO_URL]
cd MDMA-App
```

### Method 2: Manual Setup
1. Create a new folder
2. Copy all files to that folder
3. Follow steps below

## Setup

### On Windows:
1. Double-click `START.bat`
   - It will auto-install dependencies
   - It will check if Ollama is running
   - It will start the agent

### On Linux/Mac:
```bash
# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running
ollama serve

# In another terminal, pull the model
ollama pull llama3

# Run the agent
python agent.py
```

## Manual Installation
If START.bat doesn't work, install manually:

```bash
pip install langchain langgraph langchain-community
```

## Usage

Once running:
1. Type your message and press Enter
2. AI will respond
3. Type 'exit' or 'quit' to end

Example:
```
You: Hello!
AI: Hello! How can I help you today?
You: Tell me a joke
AI: [AI responds with a joke]
You: exit
```

## Troubleshooting

### "Ollama connection failed"
- Make sure Ollama is installed and running
- Run `ollama serve` in a separate terminal
- Check if model is downloaded: `ollama list`

### "Module not found"
- Run: `pip install -r requirements.txt`
- Or install manually: `pip install langchain langgraph langchain-community`

### Python not found
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

## File Structure
```
MDMA-App/
├── agent.py              # Main agent code
├── requirements.txt      # Python dependencies
├── START.bat            # Windows startup script
├── README.md            # This file
└── test_agent_input.txt # Test input file
```

## How It Works

The agent uses:
- **Langgraph**: For conversation flow and state management
- **Ollama**: Local LLM server running Llama3
- **MemorySaver**: To maintain conversation history

## Dependencies
- langchain
- langgraph
- langchain-community

## License
[Add your license here]

## Author
[Add your name here]
