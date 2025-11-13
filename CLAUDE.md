# CLAUDE.md - AI Assistant Guide for MDMA-App

## Project Overview

**MDMA-App** is a conversational AI application built with LangGraph and LangChain, designed to provide an interactive chat experience using local LLMs via Ollama.

### Purpose
This project demonstrates a simple but functional conversational AI agent with:
- Stateful conversation management using LangGraph
- Memory persistence across chat sessions
- Real-time streaming responses
- Integration with local Ollama models

## Codebase Structure

```
.
├── agent.py                 # Main application file
├── requirements.txt         # Python dependencies
├── test_agent_input.txt     # Sample test inputs
└── .git/                    # Git repository data
```

### File Descriptions

- **agent.py** (79 lines): Core application implementing the conversational AI agent
  - Defines the state management with `AgentState` TypedDict
  - Implements the `call_model` node for LLM invocation
  - Sets up the LangGraph workflow with memory persistence
  - Provides CLI-based chat interface with streaming responses

- **requirements.txt**: Lists Python package dependencies
  - `langchain` - Core LangChain framework
  - `langgraph` - Graph-based orchestration framework
  - `langchain-community` - Community integrations (ChatOllama)

- **test_agent_input.txt**: Sample conversation for testing
  - Contains example user inputs
  - Used for manual testing workflows

## Technology Stack

### Core Technologies
- **Python 3.x**: Programming language
- **LangGraph**: Stateful graph-based application framework
- **LangChain**: LLM application development framework
- **Ollama**: Local LLM server (using llama3 model)

### Key Dependencies
```python
langchain              # LLM orchestration
langgraph              # State graph management
langchain-community    # ChatOllama integration
```

## Architecture Patterns

### State Management
The application uses LangGraph's `StateGraph` pattern:

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
```

- **State**: Contains list of messages (conversation history)
- **Annotation**: Messages are accumulated (concatenated) as state updates
- **Persistence**: Uses `MemorySaver` for conversation continuity

### Graph Flow
```
[Entry Point] → [agent node] → [__end__]
     ↓              ↓
  User Input   call_model()
                    ↓
              LLM Response
```

### Node Architecture
- **Single Node Design**: `call_model` node handles all LLM interactions
- **Streaming**: Uses `stream_mode="values"` for real-time response display
- **Thread-based Sessions**: Conversations tracked via `thread_id` configuration

## Development Workflow

### Prerequisites
1. Python 3.x installed
2. Ollama running locally
3. llama3 model downloaded (`ollama pull llama3`)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# Verify llama3 model is available
ollama list
```

### Running the Application
```bash
python agent.py
```

The application will:
1. Initialize the ChatOllama model
2. Test connection to Ollama server
3. Start interactive chat loop
4. Accept user input until "exit" or "quit" is entered

### Testing
Manual testing workflow:
```bash
# Run with test input
python agent.py < test_agent_input.txt
```

## Key Conventions

### Code Style
- **Type Hints**: Use Python type annotations (TypedDict, list, etc.)
- **Docstrings**: Functions should have descriptive docstrings
- **Error Handling**: Graceful error messages with actionable guidance
- **Comments**: Explain intent, especially for configuration

### Naming Conventions
- **Functions**: `snake_case` (e.g., `call_model`)
- **Classes**: `PascalCase` (e.g., `AgentState`)
- **Constants**: `UPPER_SNAKE_CASE` (if added)
- **Variables**: `snake_case` (e.g., `user_input`, `ai_response`)

### Message Types
The application uses LangChain message types:
- `SystemMessage`: Sets context/instructions for AI
- `HumanMessage`: User inputs
- `BaseMessage`: Generic message type for state

### Configuration Pattern
```python
config = {"configurable": {"thread_id": "user-thread"}}
```
- Thread ID identifies conversation sessions
- Enables memory persistence across interactions

## Git Workflow

### Branch Strategy
- Development occurs on feature branches: `claude/claude-md-*`
- Branch naming follows pattern with session ID
- Always push to designated feature branch

### Commit Guidelines
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Write clear, descriptive commit messages
- Current commit: `fce5a7f feat: Implement conversational AI with Langgraph`

## AI Assistant Guidelines

### When Making Changes

1. **Understand Context First**
   - Read `agent.py` to understand current implementation
   - Check current state of dependencies in `requirements.txt`
   - Review git history for recent changes

2. **Code Modifications**
   - Maintain the graph-based architecture
   - Preserve type hints and annotations
   - Keep error handling for Ollama connection
   - Maintain streaming response functionality

3. **Testing Considerations**
   - Ensure Ollama connectivity is checked on startup
   - Test conversation flow with multiple exchanges
   - Verify memory persistence across messages
   - Check streaming output displays correctly

4. **Adding Features**
   - Consider adding new nodes to the graph for complex workflows
   - Use conditional edges for branching logic
   - Add tools/functions as new node types
   - Update state schema if new data needs tracking

### Common Tasks

#### Adding a New Node
```python
def new_node(state: AgentState):
    """Node description."""
    # Implementation
    return {"messages": [...]}

workflow.add_node("node_name", new_node)
workflow.add_edge("agent", "node_name")
```

#### Changing LLM Model
Update line 24 in `agent.py`:
```python
model = ChatOllama(model="model_name")  # e.g., "llama2", "mistral"
```

#### Adding Dependencies
1. Update `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Import in `agent.py` as needed

#### Extending State
```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    # Add new fields here
    context: str
    metadata: dict
```

### What to Avoid

- **Breaking Ollama Connection**: Always maintain connection error handling
- **Removing Memory**: MemorySaver is essential for conversation continuity
- **Blocking UI**: Keep streaming response for better UX
- **Hardcoded Values**: Use configuration for model names, thread IDs, etc.
- **Missing Type Hints**: Maintain type safety throughout

### Debugging Tips

1. **Ollama Issues**:
   - Check `ollama serve` is running
   - Verify model with `ollama list`
   - Test with `ollama run llama3 "test"`

2. **Graph Issues**:
   - Add print statements in nodes to trace execution
   - Check state updates are returning correct dictionary structure
   - Verify edge connections with `app.get_graph().draw_mermaid()`

3. **Memory Issues**:
   - Ensure config with thread_id is passed to all operations
   - Check MemorySaver is properly initialized
   - Verify state updates are persisting

## Future Enhancement Ideas

- Add tool calling capabilities (web search, calculations, etc.)
- Implement conditional routing based on user intent
- Add multiple LLM support with model switching
- Create web UI instead of CLI
- Add conversation export/import functionality
- Implement RAG (Retrieval Augmented Generation)
- Add logging and conversation analytics

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

---

**Last Updated**: 2025-11-13
**Current Version**: Initial implementation with single-node conversational agent
**Maintained For**: AI assistants (Claude, GPT, etc.) working on this codebase
