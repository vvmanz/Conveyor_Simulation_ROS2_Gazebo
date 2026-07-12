import os
import random
import math

from gz.transport13 import Node as GzNode
from gz.msgs10.entity_factory_pb2 import EntityFactory
from gz.msgs10.boolean_pb2 import Boolean
from gz.msgs10.quaternion_pb2 import Quaternion

from ament_index_python.packages import get_package_share_directory
from .spawn_object import SpawnObject
from .pose import Pose
from .simulation_config import (
    WORLD_NAME,
    SPAWN_X,
    SPAWN_Y,
    SPAWN_Z,
)


class ObjectSpawner:
    def __init__(self, node):
        self._node = node
        self._gz_node = GzNode()
        package_share = get_package_share_directory("conveyor_sim")
        self._models_path = os.path.join(
            package_share,
            "models",
            "cargo",
        )
        self._available_models = self._scan_models()
        self._node.get_logger().info(
            f"Available cargo models: {self._available_models}"
        )

        self._color_palette = {
            "red": "0.8 0.1 0.1 1.0",
            "green": "0.1 0.7 0.1 1.0",
            "blue": "0.1 0.1 0.8 1.0",
            "yellow": "0.9 0.8 0.1 1.0",
            "orange": "0.9 0.5 0.0 1.0",
            "purple": "0.5 0.1 0.6 1.0",
            "cyan": "0.0 0.7 0.7 1.0",
        }

        self._counter = 0

    def _scan_models(self):
        models = []
        for name in sorted(os.listdir(self._models_path)):
            path = os.path.join(self._models_path, name)
            if not os.path.isdir(path):
                continue
            if os.path.exists(os.path.join(path, "model.sdf")):
                models.append(name)
        return models
    
    def spawn(
        self,
        model,
        x,
        y,
        z,
        roll=0.0,
        pitch=0.0,
        yaw=0.0,
        name=None,
        color_rgba=None,
    ):
        if name is None:
            self._counter += 1
            name = f"{model}_{self._counter:06d}"

        model_file = os.path.join(
            self._models_path,
            model,
            "model.sdf",
        )

        if not os.path.exists(model_file):
            self._node.get_logger().error(
                f"Model '{model}' not found:\n{model_file}"
            )
            return None

        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                sdf_content = f.read()
        except Exception as e:
            self._node.get_logger().error(f"Failed to read SDF file: {e}")
            return None

        old_model_tag = f'<model name="{model}">'
        new_model_tag = f'<model name="{name}">'
        
        if old_model_tag in sdf_content:
            sdf_content = sdf_content.replace(old_model_tag, new_model_tag)
        else:
            sdf_content = sdf_content.replace(f"model name='{model}'", f"model name='{name}'")

        if color_rgba:
            sdf_content = sdf_content.replace("COLOR_MARKER", color_rgba)
        else:
            sdf_content = sdf_content.replace("COLOR_MARKER", "0.5 0.5 0.5 1.0")

        req = EntityFactory()
        req.sdf = sdf_content 
        req.name = name
        req.allow_renaming = True

        # Позиция
        req.pose.position.x = x
        req.pose.position.y = y
        req.pose.position.z = z

        # Ориентация
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q = Quaternion()
        q.w = cr * cp * cy + sr * sp * sy
        q.x = sr * cp * cy - cr * sp * sy
        q.y = cr * sp * cy + sr * cp * sy
        q.z = cr * cp * sy - sr * sp * cy

        req.pose.orientation.CopyFrom(q)

        ok, rep = self._gz_node.request(
            f"/world/{WORLD_NAME}/create",
            req,
            EntityFactory,
            Boolean,
            3000,
        )

        if not ok or not rep.data:
            self._node.get_logger().error(
                "Failed to spawn model."
            )
            return None

        self._node.get_logger().info(
            f"Spawned: {name} with color [{color_rgba if color_rgba else 'default'}]"
        )

        pose = Pose(
            x=x,
            y=y,
            z=z,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            # roll=0,
            # pitch=0,
            # yaw=0,
        )
        
        return SpawnObject(
            model=model,
            pose=pose,
            name=name,
        )

    
    def spawn_random(self):
        if not self._available_models:
            self._node.get_logger().warning(
                "No cargo models found."
            )
            return None

        model = random.choice(self._available_models)

        chosen_color_name = random.choice(list(self._color_palette.keys()))
        rgba_string = self._color_palette[chosen_color_name]

    
        # x_offset = random.uniform(-0.05, 0.05)
        x_offset = 0
        x = SPAWN_X + x_offset

        roll  = random.uniform(-0.1, 0.1)   
        pitch = random.uniform(-0.1, 0.1)   
        yaw   = random.uniform(-3.14, 3.14) 

        return self.spawn(
            model=model,
            x=x,
            y=SPAWN_Y,
            z=SPAWN_Z,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            # roll=0,
            # pitch=0,
            # yaw=0,
            color_rgba=rgba_string  # Передаем строку цвета
        )
