#!/usr/bin/env python3
"""
Jareth2 - Autonomous AI Agent with CUDA-X Acceleration

Features:
- Autonomous reasoning and action (ReAct pattern)
- Self-correction and error handling
- Full Windows control via 40 tools
- CUDA-X accelerated inference
- Memory and planning capabilities

Usage:
    python jareth2_agent.py
    python jareth2_agent.py --goal "Optimize system for gaming"
"""
import sys
import os
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from mcp_server import get_server, AlphaEdgeMCPServer


class Jareth2Agent:
    """
    Autonomous AI Agent with reasoning, planning, and tool use.

    Uses ReAct (Reasoning + Acting) pattern for autonomous problem solving.
    """

    def __init__(self, model: str = "llama33", max_iterations: int = 10):
        """
        Initialize Jareth2 agent.

        Args:
            model: Model to use (llama33, qwen, llama31)
            max_iterations: Maximum reasoning iterations
        """
        self.server = get_server()
        self.model = model
        self.max_iterations = max_iterations

        # Agent state
        self.conversation_history = []
        self.tool_results = []
        self.current_goal = None
        self.iteration = 0

        print(f"✓ Jareth2 Agent initialized")
        print(f"  Model: {model}")
        print(f"  Tools available: {len(self.server.tools)}")
        print(f"  Max iterations: {max_iterations}")

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Chat with the underlying LLM.

        Args:
            message: User message
            system_prompt: Optional system prompt

        Returns:
            LLM response
        """
        # Use local model via LM Studio
        tool_name = f"chat_{self.model}"

        args = {
            "message": message
        }

        if system_prompt:
            args["system_prompt"] = system_prompt

        result = await self.server.handle_tool_call(tool_name, args)

        if result.get("success"):
            return result.get("response", "")
        else:
            return f"Error: {result.get('error', 'Unknown error')}"

    async def think(self, observation: str) -> Dict[str, str]:
        """
        Reasoning step - analyze situation and decide next action.

        Args:
            observation: Current observation/context

        Returns:
            Dict with 'thought', 'action', 'action_input'
        """
        system_prompt = f"""You are Jareth2, an autonomous AI agent with access to 40 tools for Windows control.

Your goal: {self.current_goal}

Available tools:
{self._format_tool_list()}

You think in this format:
Thought: [Your reasoning about what to do next]
Action: [Tool name to use]
Action Input: [JSON arguments for the tool]

If you have completed the goal, use:
Thought: [Summary of what was accomplished]
Action: DONE
Action Input: {{"summary": "..."}}

Current iteration: {self.iteration}/{self.max_iterations}
"""

        # Build context from history
        context = "Previous actions:\n"
        for item in self.tool_results[-3:]:  # Last 3 actions
            context += f"- {item['action']}: {item['result']}\n"

        context += f"\nCurrent situation: {observation}"

        response = await self.chat(context, system_prompt)

        # Parse response
        return self._parse_react_response(response)

    async def act(self, action: str, action_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action using a tool.

        Args:
            action: Tool name
            action_input: Tool arguments

        Returns:
            Tool execution result
        """
        if action == "DONE":
            return {
                "success": True,
                "done": True,
                "summary": action_input.get("summary", "Task completed")
            }

        print(f"\n🔧 Action: {action}")
        print(f"   Input: {json.dumps(action_input, indent=2)}")

        try:
            result = await self.server.handle_tool_call(action, action_input)
            print(f"   ✓ Result: {self._format_result(result)}")
            return result
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            print(f"   ✗ Error: {e}")
            return error_result

    async def run_autonomous(self, goal: str) -> Dict[str, Any]:
        """
        Run agent autonomously to achieve a goal.

        Args:
            goal: High-level goal to achieve

        Returns:
            Final result with summary
        """
        self.current_goal = goal
        self.iteration = 0
        self.tool_results = []

        print(f"\n{'='*80}")
        print(f"🎯 Goal: {goal}")
        print(f"{'='*80}\n")

        observation = f"Starting task: {goal}"

        for i in range(self.max_iterations):
            self.iteration = i + 1

            print(f"\n--- Iteration {self.iteration}/{self.max_iterations} ---")

            # Think: Decide what to do
            decision = await self.think(observation)

            thought = decision.get("thought", "")
            action = decision.get("action", "")
            action_input = decision.get("action_input", {})

            print(f"\n💭 Thought: {thought}")

            # Act: Execute the action
            result = await self.act(action, action_input)

            # Record result
            self.tool_results.append({
                "iteration": self.iteration,
                "thought": thought,
                "action": action,
                "input": action_input,
                "result": result
            })

            # Check if done
            if result.get("done"):
                print(f"\n{'='*80}")
                print(f"✅ Task completed!")
                print(f"📋 Summary: {result.get('summary')}")
                print(f"{'='*80}\n")
                return {
                    "success": True,
                    "goal": goal,
                    "iterations": self.iteration,
                    "summary": result.get("summary"),
                    "actions": self.tool_results
                }

            # Prepare observation for next iteration
            if result.get("success"):
                observation = f"Action '{action}' succeeded. Result: {self._format_result(result)}"
            else:
                observation = f"Action '{action}' failed. Error: {result.get('error')}. Try a different approach."

        # Max iterations reached
        print(f"\n⚠️ Max iterations ({self.max_iterations}) reached")
        return {
            "success": False,
            "goal": goal,
            "iterations": self.iteration,
            "error": "Max iterations reached",
            "actions": self.tool_results
        }

    def _format_tool_list(self) -> str:
        """Format available tools for prompt."""
        tools = []
        for name, tool in list(self.server.tools.items())[:20]:  # Show first 20
            tools.append(f"- {name}: {tool['description'][:60]}")
        return "\n".join(tools) + "\n... (and more)"

    def _parse_react_response(self, response: str) -> Dict[str, str]:
        """Parse ReAct formatted response."""
        # Extract Thought, Action, Action Input
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', response, re.DOTALL)
        action_match = re.search(r'Action:\s*(\w+)', response)
        input_match = re.search(r'Action Input:\s*(\{.+?\})', response, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else "Thinking..."
        action = action_match.group(1).strip() if action_match else "list_processes"

        # Parse action input
        action_input = {}
        if input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except:
                pass

        return {
            "thought": thought,
            "action": action,
            "action_input": action_input
        }

    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format result for display."""
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"
            # Truncate long results
            result_str = json.dumps(result, indent=2)
            if len(result_str) > 200:
                return result_str[:200] + "..."
            return result_str
        return str(result)

    async def interactive_mode(self):
        """Interactive mode for chatting with agent."""
        print(f"\n{'='*80}")
        print("Jareth2 - Interactive Mode")
        print(f"{'='*80}")
        print("\nCommands:")
        print("  /goal <description>  - Set autonomous goal")
        print("  /tools               - List all tools")
        print("  /status              - Agent status")
        print("  /exit                - Exit")
        print(f"{'='*80}\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['/exit', '/quit']:
                    print("Goodbye! 👋")
                    break

                elif user_input.startswith('/goal '):
                    goal = user_input[6:].strip()
                    await self.run_autonomous(goal)

                elif user_input == '/tools':
                    print("\nAvailable tools:")
                    for i, (name, tool) in enumerate(self.server.tools.items(), 1):
                        print(f"{i:2d}. {name:30s} - {tool['description'][:60]}")

                elif user_input == '/status':
                    print(f"\nAgent Status:")
                    print(f"  Model: {self.model}")
                    print(f"  Current goal: {self.current_goal}")
                    print(f"  Iterations: {self.iteration}/{self.max_iterations}")
                    print(f"  Tools used: {len(self.tool_results)}")

                else:
                    # Direct chat
                    response = await self.chat(user_input)
                    print(f"\nJareth2: {response}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /exit to quit.")
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Jareth2 Autonomous AI Agent")
    parser.add_argument('--model', default='llama33', choices=['llama33', 'qwen', 'llama31'],
                        help='Model to use')
    parser.add_argument('--goal', help='Autonomous goal to achieve')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum reasoning iterations')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Interactive mode')

    args = parser.parse_args()

    # Create agent
    agent = Jareth2Agent(model=args.model, max_iterations=args.max_iterations)

    if args.goal:
        # Run with goal
        result = await agent.run_autonomous(args.goal)
        print(f"\nFinal result:")
        print(json.dumps(result, indent=2))

    elif args.interactive:
        # Interactive mode
        await agent.interactive_mode()

    else:
        # Default: interactive
        await agent.interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
