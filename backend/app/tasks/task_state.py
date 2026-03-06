"""Runtime state object for task execution.

TaskState tracks the execution context of a single task run and holds
the configuration needed to initialise the simulation engine.
"""


class TaskState:
    """In-memory state for a running task."""

    def __init__(
        self,
        task_id: str,
        task_run_id: str,
        session_id: str,
        failure_mode: str | None = None,
        simulation_type: str = "rag",
    ):
        self.task_id = task_id
        self.task_run_id = task_run_id
        self.session_id = session_id
        self.status = "pending"
        self.failure_mode = failure_mode
        self.simulation_type = simulation_type

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task_run_id": self.task_run_id,
            "session_id": self.session_id,
            "status": self.status,
            "failure_mode": self.failure_mode,
            "simulation_type": self.simulation_type,
        }
