from __future__ import annotations

import random

from app.core.config import settings
from app.tasks.definitions import TASK_DEFINITIONS


def build_task_sequence(order_mode: str) -> list[str]:
    task_ids = [definition["id"] for definition in TASK_DEFINITIONS]
    if order_mode == "randomized":
        random.Random(settings.simulation_seed).shuffle(task_ids)
    return task_ids
