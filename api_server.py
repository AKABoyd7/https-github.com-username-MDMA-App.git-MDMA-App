#!/usr/bin/env python3
"""
FastAPI REST API Server
Enterprise-grade API for Jareth2 Platform

Copyright © 2025 AlphaEdge AINV
"""
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from model_router import ModelRouter
from nvidia_integration import NVIDIANemotron, NVCLIP
from jareth2_agent import Jareth2Agent
from jareth2_daemon import Jareth2Daemon, TaskQueue


# ===== Pydantic Models =====

class ChatRequest(BaseModel):
    """Chat request"""
    query: str = Field(..., description="User query")
    task_type: Optional[str] = Field(None, description="Task type: code, business, reasoning, fast")
    context: Optional[str] = Field(None, description="Optional context")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2048, ge=1, le=8192)
    stream: bool = Field(False, description="Stream response")


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    model: str
    model_type: str
    task_type: str
    timestamp: str


class VisionRequest(BaseModel):
    """Vision request"""
    image_path: str = Field(..., description="Path to image file")
    query: Optional[str] = Field(None, description="Text query about image")
    labels: Optional[List[str]] = Field(None, description="Classification labels")


class VisionResponse(BaseModel):
    """Vision response"""
    image_path: str
    classification: Optional[Dict[str, float]] = None
    similarity: Optional[float] = None
    embedding: Optional[List[float]] = None


class ToolCallRequest(BaseModel):
    """Tool call request"""
    tool_name: str = Field(..., description="Tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ToolCallResponse(BaseModel):
    """Tool call response"""
    success: bool
    result: Any
    tool: str
    timestamp: str


class AgentTaskRequest(BaseModel):
    """Autonomous agent task"""
    goal: str = Field(..., description="Task goal")
    max_iterations: int = Field(10, ge=1, le=50)
    model: str = Field("llama33", description="Model to use")


class AgentTaskResponse(BaseModel):
    """Agent task response"""
    success: bool
    summary: str
    iterations: int
    timestamp: str


class DaemonTaskRequest(BaseModel):
    """Daemon task request"""
    goal: str = Field(..., description="Task goal")
    priority: str = Field("normal", description="Priority: low, normal, high")


class DaemonTaskResponse(BaseModel):
    """Daemon task response"""
    task_id: str
    status: str
    created_at: str


class StatusResponse(BaseModel):
    """System status"""
    status: str
    uptime: float
    models_loaded: Dict[str, Any]
    daemon_running: bool
    pending_tasks: int
    completed_tasks: int


# ===== FastAPI App =====

app = FastAPI(
    title="AlphaEdge AINV API",
    description="Enterprise AI Platform API - Jareth2",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
router: Optional[ModelRouter] = None
daemon: Optional[Jareth2Daemon] = None
task_queue: Optional[TaskQueue] = None
start_time = datetime.now()


# ===== Startup/Shutdown =====

@app.on_event("startup")
async def startup():
    """Initialize services"""
    global router, daemon, task_queue

    print("🚀 Starting AlphaEdge AINV API Server...")

    # Initialize model router
    router = ModelRouter()
    print("✓ Model router initialized")

    # Initialize task queue
    task_queue = TaskQueue()
    print("✓ Task queue initialized")

    print("✓ API Server ready!")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    print("🛑 Shutting down API Server...")


# ===== Endpoints =====

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "name": "AlphaEdge AINV API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/status", response_model=StatusResponse, tags=["General"])
async def get_status():
    """Get system status"""
    uptime = (datetime.now() - start_time).total_seconds()

    # Check daemon status
    daemon_running = False
    if task_queue:
        pending = len([t for t in task_queue.tasks if t['status'] == 'pending'])
        completed = len([t for t in task_queue.tasks if t['status'] == 'completed'])
    else:
        pending = 0
        completed = 0

    return StatusResponse(
        status="running",
        uptime=uptime,
        models_loaded=router.list_models() if router else {},
        daemon_running=daemon_running,
        pending_tasks=pending,
        completed_tasks=completed
    )


@app.post("/chat", response_model=ChatResponse, tags=["AI"])
async def chat(request: ChatRequest):
    """
    Chat with AI (auto-routed to best model)
    """
    if not router:
        raise HTTPException(500, "Router not initialized")

    try:
        result = await router.route_query(
            query=request.query,
            task_type=request.task_type,
            context=request.context,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            response=result['response'],
            model=result['model'],
            model_type=result['model_type'],
            task_type=result['task_type'],
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(500, f"Chat error: {str(e)}")


@app.post("/vision", response_model=VisionResponse, tags=["AI"])
async def vision(request: VisionRequest):
    """
    Vision query with NV-CLIP
    """
    if not router:
        raise HTTPException(500, "Router not initialized")

    try:
        result = await router.vision_query(
            image_path=request.image_path,
            query=request.query,
            labels=request.labels
        )

        return VisionResponse(**result)

    except Exception as e:
        raise HTTPException(500, f"Vision error: {str(e)}")


@app.post("/tool", response_model=ToolCallResponse, tags=["Tools"])
async def call_tool(request: ToolCallRequest):
    """
    Execute a tool
    """
    try:
        # Import server to access tools
        from mcp_server.server import get_server
        server = get_server()

        result = await server.handle_tool_call(
            request.tool_name,
            request.arguments
        )

        return ToolCallResponse(
            success=result.get('success', False),
            result=result,
            tool=request.tool_name,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(500, f"Tool error: {str(e)}")


@app.get("/tools", tags=["Tools"])
async def list_tools():
    """
    List available tools
    """
    try:
        from mcp_server.server import get_server
        server = get_server()

        return {
            "tools": list(server.tools.keys()),
            "count": len(server.tools)
        }

    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")


@app.post("/agent/task", response_model=AgentTaskResponse, tags=["Agent"])
async def agent_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    """
    Run autonomous agent task
    """
    try:
        agent = Jareth2Agent(
            model=request.model,
            max_iterations=request.max_iterations
        )

        result = await agent.run_autonomous(request.goal)

        return AgentTaskResponse(
            success=result.get('success', False),
            summary=result.get('summary', ''),
            iterations=result.get('iterations', 0),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(500, f"Agent error: {str(e)}")


@app.post("/daemon/task", response_model=DaemonTaskResponse, tags=["Daemon"])
async def add_daemon_task(request: DaemonTaskRequest):
    """
    Add task to daemon queue
    """
    if not task_queue:
        raise HTTPException(500, "Task queue not initialized")

    try:
        task_id = task_queue.add({
            'goal': request.goal,
            'priority': request.priority
        })

        return DaemonTaskResponse(
            task_id=task_id,
            status='pending',
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(500, f"Error adding task: {str(e)}")


@app.get("/daemon/tasks", tags=["Daemon"])
async def list_daemon_tasks():
    """
    List daemon tasks
    """
    if not task_queue:
        raise HTTPException(500, "Task queue not initialized")

    return {
        "tasks": task_queue.tasks,
        "total": len(task_queue.tasks)
    }


@app.get("/models", tags=["Models"])
async def list_models():
    """
    List available models
    """
    if not router:
        raise HTTPException(500, "Router not initialized")

    return router.list_models()


# ===== WebSocket =====

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time chat
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            query = data.get('query')
            task_type = data.get('task_type')

            if not query:
                await websocket.send_json({
                    'error': 'No query provided'
                })
                continue

            # Process query
            try:
                result = await router.route_query(
                    query=query,
                    task_type=task_type
                )

                await websocket.send_json({
                    'response': result['response'],
                    'model': result['model'],
                    'task_type': result['task_type']
                })

            except Exception as e:
                await websocket.send_json({
                    'error': str(e)
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ===== Main =====

def main():
    """Run server"""
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")

    print(f"""
╔════════════════════════════════════════╗
║   AlphaEdge AINV API Server           ║
║   Copyright © 2025 AlphaEdge AINV     ║
╚════════════════════════════════════════╝

Starting server on http://{host}:{port}
API Docs: http://{host}:{port}/docs
""")

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
