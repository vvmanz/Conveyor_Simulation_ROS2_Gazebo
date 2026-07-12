from dataclasses import dataclass

from .pose import Pose


@dataclass(slots=True)
class SpawnObject:
    model: str
    pose: Pose
    name: str | None = None