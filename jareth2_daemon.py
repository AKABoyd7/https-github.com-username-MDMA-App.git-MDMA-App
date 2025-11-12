#!/usr/bin/env python3
"""
Jareth2 Daemon - Background Service Mode

Runs Jareth2 as a background service that:
- Monitors system events
- Accepts task assignments
- Executes scheduled tasks
- Auto-responds to problems
- Maintains 24/7 availability

Usage:
    python jareth2_daemon.py start
    python jareth2_daemon.py stop
    python jareth2_daemon.py status
"""
import sys
import os
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import signal

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from jareth2_agent import Jareth2Agent


class TaskQueue:
    """Task queue for managing pending work"""

    def __init__(self, queue_file: str = "task_queue.json"):
        self.queue_file = Path(queue_file)
        self.tasks: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        """Load queue from disk"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                self.tasks = json.load(f)

    def save(self):
        """Save queue to disk"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add(self, task: Dict[str, Any]):
        """Add task to queue"""
        task['id'] = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task['status'] = 'pending'
        task['created_at'] = datetime.now().isoformat()
        self.tasks.append(task)
        self.save()
        return task['id']

    def get_next(self) -> Optional[Dict[str, Any]]:
        """Get next pending task"""
        for task in self.tasks:
            if task['status'] == 'pending':
                return task
        return None

    def complete(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                self.save()
                return True
        return False

    def fail(self, task_id: str, error: str):
        """Mark task as failed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'failed'
                task['failed_at'] = datetime.now().isoformat()
                task['error'] = error
                self.save()
                return True
        return False


class SystemMonitor:
    """Monitor system events and trigger auto-responses"""

    def __init__(self, agent: Jareth2Agent, queue: TaskQueue):
        self.agent = agent
        self.queue = queue
        self.thresholds = {
            'cpu_high': 90,        # CPU usage %
            'memory_high': 85,     # Memory usage %
            'disk_low': 10,        # Disk space %
            'gpu_temp_high': 85,   # GPU temp °C
        }

    async def check_system_health(self) -> List[Dict[str, Any]]:
        """Check system health and return issues"""
        issues = []

        # Check GPU temperature
        try:
            gpu_result = await self.agent.server.handle_tool_call('gpu_status', {})
            if gpu_result.get('success'):
                temp = gpu_result.get('temperature', 0)
                if temp > self.thresholds['gpu_temp_high']:
                    issues.append({
                        'type': 'gpu_temp_high',
                        'severity': 'warning',
                        'message': f'GPU temperature is {temp}°C (threshold: {self.thresholds["gpu_temp_high"]}°C)',
                        'auto_action': 'Lower GPU clock or increase fan speed'
                    })
        except:
            pass

        # Check memory usage
        try:
            sys_result = await self.agent.server.handle_tool_call('get_system_info', {})
            if sys_result.get('success'):
                mem_percent = sys_result.get('memory_percent', 0)
                if mem_percent > self.thresholds['memory_high']:
                    issues.append({
                        'type': 'memory_high',
                        'severity': 'warning',
                        'message': f'Memory usage is {mem_percent}% (threshold: {self.thresholds["memory_high"]}%)',
                        'auto_action': 'Close unnecessary processes'
                    })
        except:
            pass

        return issues

    async def auto_respond(self, issue: Dict[str, Any]):
        """Automatically respond to system issues"""
        issue_type = issue['type']

        if issue_type == 'gpu_temp_high':
            # Add task to lower GPU usage
            self.queue.add({
                'goal': 'Lower GPU temperature - close GPU-intensive processes if any',
                'priority': 'high',
                'auto_created': True,
                'trigger': issue
            })

        elif issue_type == 'memory_high':
            # Add task to free memory
            self.queue.add({
                'goal': 'Free up memory - close processes using most RAM',
                'priority': 'high',
                'auto_created': True,
                'trigger': issue
            })


class Jareth2Daemon:
    """Background daemon service for Jareth2"""

    def __init__(self):
        self.agent = Jareth2Agent(model='llama33', max_iterations=10)
        self.queue = TaskQueue()
        self.monitor = SystemMonitor(self.agent, self.queue)
        self.running = False
        self.pid_file = Path('jareth2_daemon.pid')
        self.log_file = Path('jareth2_daemon.log')

    def log(self, message: str):
        """Write to log file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_msg)

        print(log_msg.strip())

    def write_pid(self):
        """Write PID to file"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def remove_pid(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def is_running(self) -> bool:
        """Check if daemon is already running"""
        if not self.pid_file.exists():
            return False

        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())

        # Check if process exists
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            # Process doesn't exist, remove stale PID file
            self.remove_pid()
            return False

    async def process_task(self, task: Dict[str, Any]):
        """Process a single task"""
        task_id = task['id']
        goal = task['goal']

        self.log(f"Processing task {task_id}: {goal}")

        try:
            result = await self.agent.run_autonomous(goal)
            self.queue.complete(task_id, result)
            self.log(f"Task {task_id} completed successfully")
        except Exception as e:
            self.queue.fail(task_id, str(e))
            self.log(f"Task {task_id} failed: {e}")

    async def run_cycle(self):
        """Run one daemon cycle"""
        # 1. Check for pending tasks
        task = self.queue.get_next()
        if task:
            await self.process_task(task)

        # 2. Monitor system health
        issues = await self.monitor.check_system_health()
        for issue in issues:
            self.log(f"System issue detected: {issue['message']}")
            await self.monitor.auto_respond(issue)

        # 3. Check scheduled tasks
        # TODO: Implement scheduled tasks

    async def run(self):
        """Main daemon loop"""
        self.running = True
        self.write_pid()
        self.log("Jareth2 Daemon started")

        try:
            while self.running:
                await self.run_cycle()
                await asyncio.sleep(30)  # Run cycle every 30 seconds

        except KeyboardInterrupt:
            self.log("Daemon interrupted by user")
        except Exception as e:
            self.log(f"Daemon error: {e}")
        finally:
            self.running = False
            self.remove_pid()
            self.log("Jareth2 Daemon stopped")

    def start(self):
        """Start daemon"""
        if self.is_running():
            print("Jareth2 Daemon is already running")
            return

        print("Starting Jareth2 Daemon...")
        try:
            asyncio.run(self.run())
        except Exception as e:
            print(f"Failed to start daemon: {e}")

    def stop(self):
        """Stop daemon"""
        if not self.is_running():
            print("Jareth2 Daemon is not running")
            return

        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())

        print(f"Stopping Jareth2 Daemon (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        print("Daemon stopped")

    def status(self):
        """Check daemon status"""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            print(f"✓ Jareth2 Daemon is running (PID: {pid})")

            # Show queue status
            pending = len([t for t in self.queue.tasks if t['status'] == 'pending'])
            completed = len([t for t in self.queue.tasks if t['status'] == 'completed'])
            print(f"  Tasks: {pending} pending, {completed} completed")
        else:
            print("✗ Jareth2 Daemon is not running")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Jareth2 Daemon Service")
    parser.add_argument('action', choices=['start', 'stop', 'status', 'add-task'],
                        help='Daemon action')
    parser.add_argument('--goal', help='Goal for add-task action')

    args = parser.parse_args()

    daemon = Jareth2Daemon()

    if args.action == 'start':
        daemon.start()
    elif args.action == 'stop':
        daemon.stop()
    elif args.action == 'status':
        daemon.status()
    elif args.action == 'add-task':
        if not args.goal:
            print("Error: --goal required for add-task")
            return
        task_id = daemon.queue.add({'goal': args.goal})
        print(f"✓ Task added: {task_id}")


if __name__ == "__main__":
    main()
