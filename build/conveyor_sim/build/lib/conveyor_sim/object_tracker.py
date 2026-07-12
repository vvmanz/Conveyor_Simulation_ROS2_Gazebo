import time

from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V


class SpawnedObjectTracker:

    def __init__(self, ros_node, lifetime_sec=5.0):
        self._node = ros_node
        self._gz_node = GzNode()

        self._lifetime = lifetime_sec

        self._tracked = {}
        self._latest_poses = {}

        self._gz_node.subscribe(
            Pose_V,
            "/world/conveyor_world/dynamic_pose/info",
            self.pose_callback,
        )

        self._timer = self._node.create_timer(
            1.0,
            self.timer_callback,
        )

    def track(self, spawn_object):
        self._tracked[spawn_object.name] = time.time()

        self._node.get_logger().info(
            f"Tracking {spawn_object.name}"
        )

    def pose_callback(self, msg: Pose_V):
        self._latest_poses.clear()

        for pose in msg.pose:
            self._latest_poses[pose.name] = pose

    def timer_callback(self):
        now = time.time()
        remove = []
        for name, spawn_time in self._tracked.items():

            if now - spawn_time > self._lifetime:
                remove.append(name)
                continue

            pose = self._latest_poses.get(name)

            if pose is None:
                self._node.get_logger().info(
                    f"{name}: pose not found"
                )
                continue

            y = pose.position.y

            self._node.get_logger().info(
                f"{name}: y = {y:.3f}"
            )

        for name in remove:
            del self._tracked[name]

            self._node.get_logger().info(
                f"Stop tracking {name}"
            )