from dataclasses import dataclass

@dataclass(slots=True)
class Pose:
    x: float
    y: float
    z: float

    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0