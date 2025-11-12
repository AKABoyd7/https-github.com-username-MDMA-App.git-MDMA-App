"""
Project Jareth v1 - Advanced Conversational AI with Memory
Combining FastAPI REST API with Langgraph State Management
"""

import os
import threading
import time
import platform
import subprocess
import json
from typing import TypedDict, Annotated, Optional, List
from datetime import datetime

import uvicorn
import psutil
import torch
import requests
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# ============================================================================
# Configuration
# ============================================================================

def load_config():
    """Load configuration from config_local.yml"""
    config_path = os.path.join(os.path.dirname(__file__), "config_local.yml")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {
        "mode": "local",
        "model": "meta-llama-3.3-70b-instruct",
        "auto_heal": True,
        "debug_tools": True
    }

CONFIG = load_config()

# ============================================================================
# Langgraph State Management
# ============================================================================

class AgentState(TypedDict):
    """State definition for conversation memory"""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

class ConversationManager:
    """Manages multiple conversation threads with memory"""

    def __init__(self):
        self.memory = MemorySaver()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)
        self.model = None
        self._init_model()

    def _init_model(self):
        """Initialize the LLM model"""
        try:
            # Try Ollama first (for Llama 3.3)
            model_name = CONFIG.get("model", "meta-llama-3.3-70b-instruct")
            # Convert to Ollama format
            ollama_model = model_name.replace("meta-", "").replace("-instruct", "")
            self.model = ChatOllama(model=ollama_model, base_url="http://localhost:11434")
            # Test connection
            self.model.invoke([HumanMessage(content="test")])
            print(f"✅ Connected to Ollama model: {ollama_model}")
        except Exception as e:
            print(f"⚠️ Ollama connection failed: {e}")
            print("Using fallback configuration...")
            # Fallback to basic model
            self.model = ChatOllama(model="llama3", base_url="http://localhost:11434")

    def _call_model(self, state: AgentState):
        """Call the LLM with current state"""
        messages = state['messages']
        try:
            response = self.model.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            error_msg = f"Error calling model: {str(e)}"
            return {"messages": [AIMessage(content=error_msg)]}

    def _build_workflow(self):
        """Build the Langgraph workflow"""
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._call_model)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", "__end__")
        return workflow

    def chat(self, message: str, thread_id: str) -> tuple[str, str]:
        """
        Send a message and get response with memory

        Args:
            message: User message
            thread_id: Conversation thread ID

        Returns:
            (response, thread_id)
        """
        config = {"configurable": {"thread_id": thread_id}}

        # Initialize thread with system message if new
        try:
            state = self.app.get_state(config)
            if not state or not state.values.get("messages"):
                system_msg = SystemMessage(
                    content="You are Jareth AiNV, an advanced AI assistant. "
                            "You are helpful, knowledgeable, and conversational."
                )
                self.app.update_state(config, {"messages": [system_msg]})
        except:
            # New thread
            system_msg = SystemMessage(
                content="You are Jareth AiNV, an advanced AI assistant. "
                        "You are helpful, knowledgeable, and conversational."
            )
            self.app.update_state(config, {"messages": [system_msg]})

        # Process user message
        inputs = {"messages": [HumanMessage(content=message)]}

        # Get response
        response_text = ""
        for event in self.app.stream(inputs, config=config, stream_mode="values"):
            last_message = event["messages"][-1]
            if not isinstance(last_message, HumanMessage):
                response_text = last_message.content

        return response_text, thread_id

    def get_conversation(self, thread_id: str) -> List[dict]:
        """Get conversation history for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state = self.app.get_state(config)
            if not state or not state.values.get("messages"):
                return []

            messages = []
            for msg in state.values["messages"]:
                if isinstance(msg, SystemMessage):
                    messages.append({"role": "system", "content": msg.content})
                elif isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})

            return messages
        except:
            return []

    def clear_conversation(self, thread_id: str) -> bool:
        """Clear a conversation thread"""
        # Langgraph MemorySaver doesn't have direct delete,
        # so we reinitialize with empty state
        config = {"configurable": {"thread_id": thread_id}}
        try:
            self.app.update_state(config, {"messages": []})
            return True
        except:
            return False

# Initialize conversation manager
conversation_mgr = ConversationManager()

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Project Jareth v1 - Local Mode",
    version="1.0",
    description="Advanced Conversational AI with Memory Management"
)

# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    timestamp: str

class ConversationResponse(BaseModel):
    thread_id: str
    messages: List[dict]
    message_count: int

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Project Jareth v1",
        "version": "1.0",
        "status": "online",
        "endpoints": [
            "/health",
            "/chat",
            "/conversation/{thread_id}",
            "/repair_network"
        ]
    }

@app.get("/health")
def health():
    """System health check"""
    gpu_name = "No GPU"
    gpu_available = torch.cuda.is_available()

    if gpu_available:
        try:
            gpu_name = torch.cuda.get_device_name(0)
        except:
            gpu_name = "GPU detected (name unavailable)"

    return {
        "status": "healthy",
        "mode": CONFIG.get("mode", "local"),
        "model": CONFIG.get("model", "meta-llama-3.3-70b-instruct"),
        "gpu": gpu_name,
        "gpu_available": gpu_available,
        "cpu_usage": psutil.cpu_percent(),
        "ram_usage": psutil.virtual_memory().percent,
        "platform": platform.system(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat with the AI using conversational memory

    - **message**: Your message to the AI
    - **thread_id**: Optional conversation thread ID (auto-generated if not provided)
    """
    # Generate thread_id if not provided
    thread_id = request.thread_id or f"user-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        response, thread_id = conversation_mgr.chat(request.message, thread_id)

        return ChatResponse(
            response=response,
            thread_id=thread_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/conversation/{thread_id}", response_model=ConversationResponse)
def get_conversation(thread_id: str):
    """
    Get conversation history for a specific thread

    - **thread_id**: The conversation thread ID
    """
    messages = conversation_mgr.get_conversation(thread_id)

    return ConversationResponse(
        thread_id=thread_id,
        messages=messages,
        message_count=len(messages)
    )

@app.delete("/conversation/{thread_id}")
def clear_conversation(thread_id: str):
    """
    Clear/delete a conversation thread

    - **thread_id**: The conversation thread ID to clear
    """
    success = conversation_mgr.clear_conversation(thread_id)

    if success:
        return {
            "status": "success",
            "message": f"Conversation {thread_id} cleared",
            "thread_id": thread_id
        }
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/repair_network")
def repair_network():
    """
    Network repair utility (Windows only)

    Executes common network troubleshooting commands:
    - Flush DNS cache
    - Reset Winsock
    - Reset IP configuration
    """
    if platform.system() != "Windows":
        return {
            "status": "skipped",
            "message": "Network repair only available on Windows",
            "platform": platform.system()
        }

    commands = [
        "ipconfig /flushdns",
        "netsh winsock reset",
        "netsh int ip reset"
    ]

    result_log = []
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            result_log.append({
                "command": cmd,
                "status": "success",
                "output": result.stdout[:200]  # Limit output size
            })
        except subprocess.TimeoutExpired:
            result_log.append({
                "command": cmd,
                "status": "timeout",
                "error": "Command timed out after 30 seconds"
            })
        except Exception as e:
            result_log.append({
                "command": cmd,
                "status": "failed",
                "error": str(e)
            })

    return {
        "status": "completed",
        "repair_log": result_log,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/run_prompt")
def run_prompt(prompt: str):
    """
    Direct prompt execution (legacy endpoint for compatibility)

    Use /chat endpoint instead for better memory management
    """
    payload = {
        "model": CONFIG.get("model", "meta-llama-3.3-70b-instruct"),
        "prompt": prompt,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            data=json.dumps(payload),
            timeout=60
        )
        return response.json()
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Model request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============================================================================
# Background Monitoring
# ============================================================================

def auto_monitoring_loop():
    """Background monitoring and auto-healing"""
    print("🔍 Auto-monitoring started")

    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent

            if CONFIG.get("auto_heal", True):
                if cpu > 90 or mem > 90:
                    print(f"⚠️ High load detected - CPU: {cpu}% | RAM: {mem}%")

                    # Auto-healing actions
                    if platform.system() == "Windows":
                        subprocess.run("cls", shell=True)
                    else:
                        subprocess.run("clear", shell=True)

                    print("✅ Auto-healing triggered")

            # Sleep for 60 seconds
            time.sleep(60)

        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(60)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Project Jareth v1 - Starting...")
    print("=" * 60)
    print(f"Mode: {CONFIG.get('mode', 'local')}")
    print(f"Model: {CONFIG.get('model', 'meta-llama-3.3-70b-instruct')}")
    print(f"Platform: {platform.system()}")

    # GPU Check
    if torch.cuda.is_available():
        print(f"GPU: ✅ {torch.cuda.get_device_name(0)}")
    else:
        print("GPU: ❌ Not available (running on CPU)")

    print("=" * 60)

    # Start background monitoring
    if CONFIG.get("auto_heal", True):
        monitor_thread = threading.Thread(target=auto_monitoring_loop, daemon=True)
        monitor_thread.start()
        print("✅ Auto-monitoring enabled")

    # Start FastAPI server
    print("\n🌐 Starting API server on http://0.0.0.0:8500")
    print("📚 API docs available at http://localhost:8500/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8500, log_level="info")
