#!/usr/bin/env python3
"""
Multi-Agent Orchestration Framework
Coordinate multiple AI agents for complex tasks

Copyright © 2025 AlphaEdge AINV
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
import json


class AgentRole(Enum):
    """Agent roles"""
    COORDINATOR = "coordinator"  # Manages other agents
    RESEARCHER = "researcher"    # Gathers information
    CODER = "coder"             # Writes code
    ANALYST = "analyst"         # Analyzes data
    EXECUTOR = "executor"       # Executes actions
    REVIEWER = "reviewer"       # Reviews work


class AgentStatus(Enum):
    """Agent status"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class Agent:
    """
    Individual agent in the multi-agent system
    """

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        model: str = "llama33",
        capabilities: Optional[List[str]] = None
    ):
        """
        Initialize agent

        Args:
            agent_id: Unique agent ID
            role: Agent role
            model: LLM model to use
            capabilities: List of capabilities
        """
        self.agent_id = agent_id
        self.role = role
        self.model = model
        self.capabilities = capabilities or []
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Dict[str, Any]] = None
        self.results: List[Dict[str, Any]] = []

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task

        Args:
            task: Task definition

        Returns:
            Task result
        """
        self.status = AgentStatus.WORKING
        self.current_task = task

        try:
            # Import here to avoid circular dependency
            from jareth2_agent import Jareth2Agent

            # Create agent
            agent = Jareth2Agent(model=self.model, max_iterations=10)

            # Execute task
            result = await agent.run_autonomous(task['goal'])

            # Store result
            result['agent_id'] = self.agent_id
            result['agent_role'] = self.role.value
            result['timestamp'] = datetime.now().isoformat()

            self.results.append(result)
            self.status = AgentStatus.COMPLETED

            return result

        except Exception as e:
            self.status = AgentStatus.FAILED
            error_result = {
                'success': False,
                'error': str(e),
                'agent_id': self.agent_id,
                'agent_role': self.role.value,
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(error_result)
            return error_result

        finally:
            self.current_task = None

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type"""
        if not self.capabilities:
            return True  # Generic agent

        return task_type in self.capabilities

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'status': self.status.value,
            'current_task': self.current_task,
            'completed_tasks': len([r for r in self.results if r.get('success')])
        }


class MultiAgentOrchestrator:
    """
    Orchestrate multiple agents for complex workflows
    """

    def __init__(self):
        """Initialize orchestrator"""
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.running = False

    def add_agent(self, agent: Agent):
        """Add agent to orchestrator"""
        self.agents[agent.agent_id] = agent
        print(f"✓ Agent added: {agent.agent_id} ({agent.role.value})")

    def create_agent(
        self,
        agent_id: str,
        role: AgentRole,
        model: str = "llama33",
        capabilities: Optional[List[str]] = None
    ) -> Agent:
        """
        Create and add agent

        Args:
            agent_id: Agent ID
            role: Agent role
            model: Model to use
            capabilities: Agent capabilities

        Returns:
            Created agent
        """
        agent = Agent(agent_id, role, model, capabilities)
        self.add_agent(agent)
        return agent

    def add_task(
        self,
        goal: str,
        task_type: str = "general",
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        assigned_agent: Optional[str] = None
    ) -> str:
        """
        Add task to queue

        Args:
            goal: Task goal
            task_type: Type of task
            priority: Priority (higher = more urgent)
            dependencies: List of task IDs that must complete first
            assigned_agent: Specific agent to use (optional)

        Returns:
            Task ID
        """
        task_id = f"task_{len(self.task_queue) + len(self.completed_tasks)}"

        task = {
            'id': task_id,
            'goal': goal,
            'type': task_type,
            'priority': priority,
            'dependencies': dependencies or [],
            'assigned_agent': assigned_agent,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x['priority'], reverse=True)

        return task_id

    def get_available_agent(self, task: Dict[str, Any]) -> Optional[Agent]:
        """
        Get available agent for task

        Args:
            task: Task definition

        Returns:
            Available agent or None
        """
        # Check if specific agent assigned
        if task.get('assigned_agent'):
            agent = self.agents.get(task['assigned_agent'])
            if agent and agent.status == AgentStatus.IDLE:
                return agent
            return None

        # Find idle agent that can handle task
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE and agent.can_handle(task['type']):
                return agent

        return None

    def check_dependencies(self, task: Dict[str, Any]) -> bool:
        """
        Check if task dependencies are met

        Args:
            task: Task definition

        Returns:
            True if dependencies met
        """
        if not task['dependencies']:
            return True

        # Check if all dependencies completed
        completed_ids = [t['id'] for t in self.completed_tasks]

        for dep_id in task['dependencies']:
            if dep_id not in completed_ids:
                return False

        return True

    async def process_tasks(self):
        """Process task queue"""
        while self.task_queue:
            # Get next task
            task = None

            for t in self.task_queue:
                if self.check_dependencies(t):
                    task = t
                    break

            if not task:
                # No tasks with met dependencies
                await asyncio.sleep(1)
                continue

            # Get agent
            agent = self.get_available_agent(task)

            if not agent:
                # No available agent
                await asyncio.sleep(1)
                continue

            # Remove from queue
            self.task_queue.remove(task)

            # Execute task
            print(f"🤖 Agent {agent.agent_id} executing: {task['goal']}")

            result = await agent.execute_task(task)

            task['result'] = result
            task['status'] = 'completed' if result.get('success') else 'failed'
            task['completed_at'] = datetime.now().isoformat()

            self.completed_tasks.append(task)

            print(f"✓ Task completed: {task['id']}")

    async def run_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a workflow (sequence of tasks)

        Args:
            workflow: List of task definitions

        Returns:
            Workflow results
        """
        print(f"🚀 Starting workflow with {len(workflow)} tasks")

        # Add all tasks
        task_ids = []
        for task_def in workflow:
            task_id = self.add_task(**task_def)
            task_ids.append(task_id)

        # Process tasks
        await self.process_tasks()

        # Gather results
        results = {
            'workflow_id': f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'total_tasks': len(task_ids),
            'completed': len([t for t in self.completed_tasks if t['id'] in task_ids]),
            'failed': len([
                t for t in self.completed_tasks
                if t['id'] in task_ids and t['status'] == 'failed'
            ]),
            'tasks': [
                t for t in self.completed_tasks
                if t['id'] in task_ids
            ]
        }

        return results

    async def parallel_execution(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel

        Args:
            tasks: List of task definitions

        Returns:
            List of results
        """
        print(f"⚡ Parallel execution: {len(tasks)} tasks")

        # Assign tasks to agents
        task_futures = []

        for task_def in tasks:
            agent = self.get_available_agent(task_def)

            if agent:
                future = agent.execute_task(task_def)
                task_futures.append(future)
            else:
                print(f"⚠ No available agent for task: {task_def['goal']}")

        # Wait for all
        results = await asyncio.gather(*task_futures, return_exceptions=True)

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'agents': {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            },
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'running': self.running
        }


# ===== Global Orchestrator =====

_orchestrator: Optional[MultiAgentOrchestrator] = None


def get_orchestrator() -> MultiAgentOrchestrator:
    """Get global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator


# ===== Convenience Functions =====

def create_default_team() -> MultiAgentOrchestrator:
    """
    Create default agent team

    Returns:
        Orchestrator with default agents
    """
    orchestrator = MultiAgentOrchestrator()

    # Coordinator
    orchestrator.create_agent(
        "coordinator",
        AgentRole.COORDINATOR,
        model="llama33"
    )

    # Coder
    orchestrator.create_agent(
        "coder",
        AgentRole.CODER,
        model="qwen",
        capabilities=["code", "programming", "debugging"]
    )

    # Analyst
    orchestrator.create_agent(
        "analyst",
        AgentRole.ANALYST,
        model="llama33",
        capabilities=["analysis", "data", "research"]
    )

    # Executor
    orchestrator.create_agent(
        "executor",
        AgentRole.EXECUTOR,
        model="llama31",
        capabilities=["execution", "tools", "system"]
    )

    return orchestrator


# ===== CLI =====

if __name__ == "__main__":
    async def test_multi_agent():
        print("=== Testing Multi-Agent System ===\n")

        # Create team
        orchestrator = create_default_team()

        # Define workflow
        workflow = [
            {
                'goal': 'Research best practices for Python error handling',
                'task_type': 'research',
                'priority': 2
            },
            {
                'goal': 'Write a Python function with proper error handling',
                'task_type': 'code',
                'priority': 1,
                'dependencies': []  # Depends on research
            }
        ]

        # Run workflow
        results = await orchestrator.run_workflow(workflow)

        print(f"\n✓ Workflow completed")
        print(f"  Total: {results['total_tasks']}")
        print(f"  Completed: {results['completed']}")
        print(f"  Failed: {results['failed']}")

    asyncio.run(test_multi_agent())
