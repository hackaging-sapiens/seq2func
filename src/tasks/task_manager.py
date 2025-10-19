"""
Task manager for async gene search operations.

Manages background tasks with progress tracking and cancellation support.
"""

import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ProgressInfo:
    """Progress information for a running task."""
    current_step: str
    step_number: int
    total_steps: int
    papers_screened: Optional[int] = None
    total_papers: Optional[int] = None
    message: str = ""


@dataclass
class TaskInfo:
    """Information about a task."""
    task_id: str
    status: str  # pending, running, completed, cancelled, failed
    progress: Optional[ProgressInfo] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        if self.progress:
            data["progress"] = {
                "current_step": self.progress.current_step,
                "step_number": self.progress.step_number,
                "total_steps": self.progress.total_steps,
                "papers_screened": self.progress.papers_screened,
                "total_papers": self.progress.total_papers,
                "message": self.progress.message,
            }

        if self.result is not None:
            data["result"] = self.result

        if self.error is not None:
            data["error"] = self.error

        return data


class CancellationToken:
    """Token that can be checked to see if a task should be cancelled."""

    def __init__(self):
        self._cancelled = False
        self._lock = threading.Lock()

    def cancel(self):
        """Mark this token as cancelled."""
        with self._lock:
            self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if this token has been cancelled."""
        with self._lock:
            return self._cancelled


class ProgressCallback:
    """Callback for reporting progress updates."""

    def __init__(self, task_id: str, task_manager: 'TaskManager'):
        self.task_id = task_id
        self.task_manager = task_manager

    def update(
        self,
        current_step: str,
        step_number: int,
        total_steps: int = 4,
        papers_screened: Optional[int] = None,
        total_papers: Optional[int] = None,
        message: str = ""
    ):
        """Update the progress of the task."""
        progress = ProgressInfo(
            current_step=current_step,
            step_number=step_number,
            total_steps=total_steps,
            papers_screened=papers_screened,
            total_papers=total_papers,
            message=message
        )
        self.task_manager.update_progress(self.task_id, progress)


class TaskManager:
    """Manages background tasks with progress tracking and cancellation."""

    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self.cancellation_tokens: Dict[str, CancellationToken] = {}
        self._lock = threading.Lock()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_tasks, daemon=True)
        self._cleanup_thread.start()

    def create_task(self) -> tuple[str, CancellationToken, ProgressCallback]:
        """
        Create a new task and return its ID, cancellation token, and progress callback.

        Returns:
            tuple: (task_id, cancellation_token, progress_callback)
        """
        task_id = str(uuid.uuid4())
        cancellation_token = CancellationToken()

        with self._lock:
            self.tasks[task_id] = TaskInfo(
                task_id=task_id,
                status="pending"
            )
            self.cancellation_tokens[task_id] = cancellation_token

        progress_callback = ProgressCallback(task_id, self)

        return task_id, cancellation_token, progress_callback

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information by ID."""
        with self._lock:
            return self.tasks.get(task_id)

    def update_status(self, task_id: str, status: str):
        """Update the status of a task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                self.tasks[task_id].updated_at = datetime.now()

    def update_progress(self, task_id: str, progress: ProgressInfo):
        """Update the progress of a task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = progress
                self.tasks[task_id].status = "running"
                self.tasks[task_id].updated_at = datetime.now()

    def set_result(self, task_id: str, result: Any):
        """Set the result of a completed task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].result = result
                self.tasks[task_id].status = "completed"
                self.tasks[task_id].updated_at = datetime.now()

    def set_error(self, task_id: str, error: str):
        """Set the error for a failed task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].error = error
                self.tasks[task_id].status = "failed"
                self.tasks[task_id].updated_at = datetime.now()

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.

        Returns:
            bool: True if task was found and cancellation was initiated, False otherwise
        """
        with self._lock:
            if task_id in self.cancellation_tokens:
                self.cancellation_tokens[task_id].cancel()
                if task_id in self.tasks:
                    self.tasks[task_id].status = "cancelled"
                    self.tasks[task_id].updated_at = datetime.now()
                return True
            return False

    def _cleanup_old_tasks(self):
        """Background thread that cleans up old tasks (>1 hour old)."""
        while True:
            try:
                threading.Event().wait(300)  # Check every 5 minutes

                cutoff_time = datetime.now() - timedelta(hours=1)

                with self._lock:
                    # Find old completed/cancelled/failed tasks
                    tasks_to_remove = [
                        task_id for task_id, task in self.tasks.items()
                        if task.status in ["completed", "cancelled", "failed"]
                        and task.updated_at < cutoff_time
                    ]

                    # Remove them
                    for task_id in tasks_to_remove:
                        del self.tasks[task_id]
                        if task_id in self.cancellation_tokens:
                            del self.cancellation_tokens[task_id]

            except Exception as e:
                print(f"Error in cleanup thread: {e}")
