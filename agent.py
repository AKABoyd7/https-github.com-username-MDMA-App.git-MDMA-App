import os
import warnings
# Suppress compatibility warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from typing import TypedDict, Annotated
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]

# Define the nodes for our graph
def call_model(state: AgentState):
    """Calls the LLM to generate a response."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Set up the model, assuming a local Ollama server is running
# You can change the model name to whichever model you have available
# Set up the model, assuming a local Ollama server is running
# You can change the model name to whichever model you have available
try:
    model = ChatOllama(model="llama3")
    # Ping the model to ensure it's available
    model.invoke("test")
except Exception as e:
    print(f"Failed to connect to Ollama. Please ensure Ollama is running and the 'llama3' model is available.")
    print("You can download it by running 'ollama pull llama3'")
    exit()

# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("agent", call_model)

# Set the entrypoint
workflow.set_entry_point("agent")

# Add the edges. In this simple case, we loop back to the user for more input.
# The graph will end when the user types 'exit' or 'quit'.
workflow.add_edge("agent", "__end__")

# Compile the graph
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Main execution loop
if __name__ == "__main__":
    print("Agent is running... Type 'exit' or 'quit' to end the conversation.")

    # The config is necessary for the memory saver to correctly track the conversation
    config = {"configurable": {"thread_id": "user-thread"}}

    # Add a system message to set the context for the AI
    system_message = SystemMessage(content="You are a helpful AI assistant.")
    app.update_state(config, {"messages": [system_message]})

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting agent.")
            break

        inputs = {"messages": [HumanMessage(content=user_input)]}

        # We stream the response so the user sees the output as it's generated
        for event in app.stream(inputs, config=config, stream_mode="values"):
            # The 'values' stream mode returns the full state at each step
            ai_response = event["messages"][-1]
            if isinstance(ai_response, HumanMessage):
                # The last message is the user's, so the AI hasn't responded yet.
                continue

            # Clear the line and print the AI's response
            print(f"\rAI: {ai_response.content}", end="", flush=True)
        print() # Move to the next line after the AI is done responding
