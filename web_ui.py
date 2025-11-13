#!/usr/bin/env python3
"""
Gradio Web UI for Jareth2 Platform
Enterprise-grade web interface

Copyright © 2025 AlphaEdge AINV
"""
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

import gradio as gr

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from model_router import ModelRouter
from jareth2_agent import Jareth2Agent
from jareth2_daemon import TaskQueue
from nvidia_integration import NVCLIP


# ===== Global State =====

router: Optional[ModelRouter] = None
task_queue: Optional[TaskQueue] = None
chat_history: List[Tuple[str, str]] = []


def initialize():
    """Initialize components"""
    global router, task_queue

    if router is None:
        router = ModelRouter()
        print("✓ Model router initialized")

    if task_queue is None:
        task_queue = TaskQueue()
        print("✓ Task queue initialized")


# ===== Chat Interface =====

async def chat_async(
    message: str,
    history: List[Tuple[str, str]],
    task_type: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> Tuple[List[Tuple[str, str]], str]:
    """
    Process chat message

    Args:
        message: User message
        history: Chat history
        task_type: Task type selection
        model: Model selection
        temperature: Sampling temperature
        max_tokens: Max tokens

    Returns:
        Updated history and empty string
    """
    initialize()

    try:
        # Route query
        task_type_map = {
            "Auto-detect": None,
            "Code": "code",
            "Business": "business",
            "Reasoning": "reasoning",
            "Fast": "fast"
        }

        result = await router.route_query(
            query=message,
            task_type=task_type_map.get(task_type),
            temperature=temperature,
            max_tokens=max_tokens
        )

        response = result['response']
        model_used = result['model']

        # Add to history
        history.append((message, f"**[{model_used}]** {response}"))

        return history, ""

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append((message, error_msg))
        return history, ""


def chat(
    message: str,
    history: List[Tuple[str, str]],
    task_type: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> Tuple[List[Tuple[str, str]], str]:
    """Sync wrapper for chat"""
    return asyncio.run(chat_async(message, history, task_type, model, temperature, max_tokens))


# ===== Tool Interface =====

async def call_tool_async(tool_name: str, arguments: str) -> str:
    """
    Call a tool

    Args:
        tool_name: Tool to call
        arguments: JSON arguments

    Returns:
        Tool result
    """
    try:
        from mcp_server.server import get_server
        import json

        server = get_server()

        # Parse arguments
        if arguments.strip():
            args = json.loads(arguments)
        else:
            args = {}

        # Call tool
        result = await server.handle_tool_call(tool_name, args)

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"❌ Error: {str(e)}"


def call_tool(tool_name: str, arguments: str) -> str:
    """Sync wrapper for tool call"""
    return asyncio.run(call_tool_async(tool_name, arguments))


def list_tools() -> str:
    """List available tools"""
    try:
        from mcp_server.server import get_server
        server = get_server()

        tools = list(server.tools.keys())
        return "\n".join([f"• {tool}" for tool in sorted(tools)])

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ===== Agent Interface =====

async def run_agent_async(goal: str, max_iterations: int, model: str) -> str:
    """
    Run autonomous agent

    Args:
        goal: Task goal
        max_iterations: Max iterations
        model: Model to use

    Returns:
        Agent result
    """
    try:
        agent = Jareth2Agent(model=model, max_iterations=max_iterations)

        result = await agent.run_autonomous(goal)

        if result.get('success'):
            return f"""✅ **Task Completed**

**Summary:** {result.get('summary', 'N/A')}

**Iterations:** {result.get('iterations', 0)}
"""
        else:
            return f"❌ **Task Failed**\n\n{result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def run_agent(goal: str, max_iterations: int, model: str) -> str:
    """Sync wrapper for agent"""
    return asyncio.run(run_agent_async(goal, max_iterations, model))


# ===== Daemon Interface =====

def add_daemon_task(goal: str, priority: str) -> str:
    """Add task to daemon queue"""
    initialize()

    try:
        task_id = task_queue.add({
            'goal': goal,
            'priority': priority
        })

        return f"✅ Task added: {task_id}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def list_daemon_tasks() -> str:
    """List daemon tasks"""
    initialize()

    try:
        tasks = task_queue.tasks

        if not tasks:
            return "No tasks in queue"

        output = []
        for task in tasks:
            status_icon = {
                'pending': '⏳',
                'completed': '✅',
                'failed': '❌'
            }.get(task['status'], '❓')

            output.append(f"{status_icon} **{task['id']}** - {task['goal']} ({task['status']})")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ===== Vision Interface =====

async def vision_query_async(image_path: str, query: str, labels: str) -> str:
    """
    Vision query with NV-CLIP

    Args:
        image_path: Path to image
        query: Text query
        labels: Comma-separated labels

    Returns:
        Vision results
    """
    initialize()

    try:
        # Parse labels
        label_list = [l.strip() for l in labels.split(',')] if labels.strip() else None

        # Query
        result = await router.vision_query(
            image_path=image_path,
            query=query if query.strip() else None,
            labels=label_list
        )

        output = [f"**Image:** {result['image_path']}"]

        if 'classification' in result and result['classification']:
            output.append("\n**Classification:**")
            for label, score in sorted(result['classification'].items(), key=lambda x: x[1], reverse=True):
                output.append(f"  • {label}: {score:.2%}")

        if 'similarity' in result and result['similarity'] is not None:
            output.append(f"\n**Similarity:** {result['similarity']:.2%}")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error: {str(e)}"


def vision_query(image_path: str, query: str, labels: str) -> str:
    """Sync wrapper for vision query"""
    return asyncio.run(vision_query_async(image_path, query, labels))


# ===== System Status =====

def get_system_status() -> str:
    """Get system status"""
    initialize()

    try:
        # Models
        models = router.list_models()
        local_count = len(models.get('local', []))
        cloud_count = len(models.get('cloud', []))
        multimodal_count = len(models.get('multimodal', []))

        # Tasks
        pending = len([t for t in task_queue.tasks if t['status'] == 'pending'])
        completed = len([t for t in task_queue.tasks if t['status'] == 'completed'])
        failed = len([t for t in task_queue.tasks if t['status'] == 'failed'])

        return f"""**System Status**

**Models:**
  • Local: {local_count}
  • Cloud: {cloud_count}
  • Multimodal: {multimodal_count}

**Daemon Queue:**
  • Pending: {pending}
  • Completed: {completed}
  • Failed: {failed}

**Status:** ✅ Running
"""

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ===== Gradio Interface =====

def create_ui():
    """Create Gradio UI"""

    # Custom NVIDIA Green theme
    # All green - NVIDIA Green everywhere, Dark gray background
    custom_theme = gr.themes.Base(
        primary_hue=gr.themes.colors.green,  # NVIDIA Green for everything
        secondary_hue=gr.themes.colors.green,  # NVIDIA Green (no purple!)
        neutral_hue=gr.themes.colors.slate,  # Dark gray background
    ).set(
        body_background_fill="#1a1a1a",  # Very dark gray background
        body_background_fill_dark="#0f0f0f",  # Almost black for dark mode
        button_primary_background_fill="#10b981",  # NVIDIA Green buttons
        button_primary_background_fill_hover="#059669",  # Darker NVIDIA Green on hover
        button_primary_text_color="white",
        slider_color="#10b981",  # NVIDIA Green sliders
        block_title_text_color="#10b981",  # NVIDIA Green titles
        block_label_text_color="#d1d5db",  # Light gray labels
        block_background_fill="#262626",  # Dark gray blocks
        input_background_fill="#1f1f1f",  # Dark input backgrounds
        input_border_color="#404040",  # Subtle borders
    )

    with gr.Blocks(
        title="AlphaEdge AINV - Jareth2",
        theme=custom_theme,
        css="""
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a1a !important;
        }
        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%); /* NVIDIA Green gradient */
            color: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(16, 185, 129, 0.4);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            margin: 10px 0 5px 0;
            font-size: 1.1em;
            opacity: 0.95;
        }
        .header small {
            opacity: 0.8;
        }
        /* Green accents for buttons and interactive elements */
        .primary {
            background-color: #10b981 !important;
            border-color: #10b981 !important;
        }
        .primary:hover {
            background-color: #059669 !important;
        }
        /* NVIDIA branding elements - All Green */
        .nvidia-badge {
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #059669); /* NVIDIA Green */
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 8px;
        }
        /* Dark theme for all components */
        .gr-box, .gr-form, .gr-input {
            background-color: #262626 !important;
            border-color: #404040 !important;
        }
        """
    ) as demo:

        # Header
        gr.HTML("""
        <div class="header">
            <h1>🤖 AlphaEdge AINV - Jareth2 <span class="nvidia-badge">NVIDIA Powered</span></h1>
            <p>Enterprise AI Platform | The Interface of Freedom™</p>
            <small>Copyright © 2025 AlphaEdge AINV | Powered by NVIDIA TensorRT & CUDA-X</small>
        </div>
        """)

        # Tabs
        with gr.Tabs():

            # === Chat Tab ===
            with gr.Tab("💬 Chat"):
                gr.Markdown("### Chat with AI (Auto-routed)")

                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(label="Conversation", height=500)
                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            lines=2
                        )
                        send_btn = gr.Button("Send", variant="primary")

                    with gr.Column(scale=1):
                        task_type = gr.Dropdown(
                            choices=["Auto-detect", "Code", "Business", "Reasoning", "Fast"],
                            value="Auto-detect",
                            label="Task Type"
                        )
                        model_select = gr.Dropdown(
                            choices=["auto", "llama-3.3-70B", "qwen-2.5-coder-32B", "nemotron-3-43B"],
                            value="auto",
                            label="Model (auto = best)"
                        )
                        temperature = gr.Slider(0.0, 2.0, 0.7, step=0.1, label="Temperature")
                        max_tokens = gr.Slider(128, 8192, 2048, step=128, label="Max Tokens")

                send_btn.click(
                    chat,
                    inputs=[msg, chatbot, task_type, model_select, temperature, max_tokens],
                    outputs=[chatbot, msg]
                )
                msg.submit(
                    chat,
                    inputs=[msg, chatbot, task_type, model_select, temperature, max_tokens],
                    outputs=[chatbot, msg]
                )

            # === Tools Tab ===
            with gr.Tab("🛠️ Tools"):
                gr.Markdown("### Execute Tools Directly")

                with gr.Row():
                    with gr.Column():
                        tool_list_btn = gr.Button("List All Tools")
                        tool_list_output = gr.Textbox(label="Available Tools", lines=15)

                    with gr.Column():
                        tool_name = gr.Textbox(label="Tool Name", placeholder="e.g., gpu_status")
                        tool_args = gr.Textbox(
                            label="Arguments (JSON)",
                            placeholder='{"arg1": "value1"}',
                            lines=3
                        )
                        tool_exec_btn = gr.Button("Execute", variant="primary")
                        tool_result = gr.Textbox(label="Result", lines=15)

                tool_list_btn.click(list_tools, outputs=tool_list_output)
                tool_exec_btn.click(call_tool, inputs=[tool_name, tool_args], outputs=tool_result)

            # === Agent Tab ===
            with gr.Tab("🤖 Autonomous Agent"):
                gr.Markdown("### Run Autonomous Tasks")

                agent_goal = gr.Textbox(
                    label="Goal",
                    placeholder="e.g., Check GPU status and optimize if needed",
                    lines=2
                )

                with gr.Row():
                    agent_iterations = gr.Slider(1, 50, 10, step=1, label="Max Iterations")
                    agent_model = gr.Dropdown(
                        choices=["llama33", "qwen", "llama31"],
                        value="llama33",
                        label="Model"
                    )

                agent_run_btn = gr.Button("Run Agent", variant="primary")
                agent_result = gr.Textbox(label="Result", lines=20)

                agent_run_btn.click(
                    run_agent,
                    inputs=[agent_goal, agent_iterations, agent_model],
                    outputs=agent_result
                )

            # === Daemon Tab ===
            with gr.Tab("⚙️ Daemon Queue"):
                gr.Markdown("### 24/7 Background Task Queue")

                with gr.Row():
                    with gr.Column():
                        daemon_goal = gr.Textbox(label="Task Goal", lines=2)
                        daemon_priority = gr.Dropdown(
                            choices=["low", "normal", "high"],
                            value="normal",
                            label="Priority"
                        )
                        daemon_add_btn = gr.Button("Add Task", variant="primary")
                        daemon_add_result = gr.Textbox(label="Result", lines=2)

                    with gr.Column():
                        daemon_list_btn = gr.Button("Refresh Task List")
                        daemon_tasks = gr.Textbox(label="Task Queue", lines=15)

                daemon_add_btn.click(
                    add_daemon_task,
                    inputs=[daemon_goal, daemon_priority],
                    outputs=daemon_add_result
                )
                daemon_list_btn.click(list_daemon_tasks, outputs=daemon_tasks)

            # === Vision Tab ===
            with gr.Tab("👁️ Vision (NV-CLIP)"):
                gr.Markdown("### Multimodal Vision Analysis")

                vision_image = gr.Textbox(label="Image Path", placeholder="G:/path/to/image.jpg")
                vision_query_text = gr.Textbox(
                    label="Query (optional)",
                    placeholder="What is in this image?"
                )
                vision_labels = gr.Textbox(
                    label="Classification Labels (optional, comma-separated)",
                    placeholder="person, car, building, nature"
                )

                vision_btn = gr.Button("Analyze", variant="primary")
                vision_result = gr.Textbox(label="Result", lines=15)

                vision_btn.click(
                    vision_query,
                    inputs=[vision_image, vision_query_text, vision_labels],
                    outputs=vision_result
                )

            # === Status Tab ===
            with gr.Tab("📊 System Status"):
                gr.Markdown("### System Information")

                status_btn = gr.Button("Refresh Status")
                status_output = gr.Textbox(label="Status", lines=20)

                status_btn.click(get_system_status, outputs=status_output)

                # Auto-refresh on load
                demo.load(get_system_status, outputs=status_output)

        # Footer
        gr.Markdown("""
        ---
        **AlphaEdge AINV - Jareth2** | Copyright © 2025 AlphaEdge AINV | All Rights Reserved
        """)

    return demo


# ===== Main =====

def main():
    """Run web UI"""
    print("""
╔════════════════════════════════════════╗
║   AlphaEdge AINV - Jareth2 Web UI     ║
║   Copyright © 2025 AlphaEdge AINV     ║
╚════════════════════════════════════════╝
""")

    # Initialize
    initialize()

    # Create and launch UI
    demo = create_ui()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
