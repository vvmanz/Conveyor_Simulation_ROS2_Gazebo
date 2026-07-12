import json


import cv2
import numpy as np
from cv_bridge import CvBridge

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image

from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
JSON_PATH = PACKAGE_DIR / "spawned_objects.json"

WORKSPACE = Path(__file__).resolve().parents[3]
DATASET_DIR = WORKSPACE / "dataset_ozon"


Y_MAX = 2.50
Y_MIN = 1.60
NUM_IMAGES = 10


class DatasetRecorder(Node):

    def __init__(self):
        super().__init__("dataset_recorder")

        self.bridge = CvBridge()

        self.rgb_image = None
        self.depth_image = None

        self.tracked = {}

        # имя объекта -> следующий индекс снимка
        self.capture_index = {}

        self.capture_points = np.linspace(
            Y_MAX,
            Y_MIN,
            NUM_IMAGES,
        )

        self.gz_node = GzNode()

        self.gz_node.subscribe(
            Pose_V,
            "/world/conveyor_world/dynamic_pose/info",
            self.pose_callback,
        )

        self.create_subscription(
            Image,
            "/camera/image_raw",
            self.rgb_callback,
            qos_profile_sensor_data,
        )

        self.create_subscription(
            Image,
            "/camera/depth_raw",
            self.depth_callback,
            qos_profile_sensor_data,
        )

        self.create_timer(
            1.0,
            self.load_registry,
        )

        self.get_logger().info("Dataset recorder started.")

        self.get_logger().info(
            f"Capture positions: {self.capture_points}"
        )

    def load_registry(self):

        if not JSON_PATH.exists():
            self.tracked = {}
            return

        try:
            with open(JSON_PATH, "r") as f:
                self.tracked = json.load(f)
        except Exception:
            self.tracked = {}

    def rgb_callback(self, msg):
        self.rgb_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding="bgr8",
        )

    def depth_callback(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding="passthrough",
        )

    def pose_callback(self, msg):

        if self.rgb_image is None:
            return

        if self.depth_image is None:
            return

        for pose in msg.pose:

            name = pose.name

            if name not in self.tracked:
                continue

            if name not in self.capture_index:
                self.capture_index[name] = 0

            index = self.capture_index[name]

            if index >= NUM_IMAGES:
                continue

            y = pose.position.y

            target_y = self.capture_points[index]

            if y > target_y:
                continue

            object_dir = DATASET_DIR / name
            rgb_dir = object_dir / "rgb"
            depth_dir = object_dir / "depth"

            rgb_dir.mkdir(parents=True, exist_ok=True)
            depth_dir.mkdir(parents=True, exist_ok=True)

            rgb_path = rgb_dir / f"{index:03d}.png"
            depth_path = depth_dir / f"{index:03d}.npy"

            cv2.imwrite(
                str(rgb_path),
                self.rgb_image,
            )

            np.save(
                depth_path,
                self.depth_image,
            )

            self.capture_index[name] += 1

            self.get_logger().info(
                f"{name}: saved {index+1}/{NUM_IMAGES}  y={y:.3f}"
            )

            if self.capture_index[name] == NUM_IMAGES:
                self.get_logger().info(
                    f"{name}: capture complete."
                )


def main():

    rclpy.init()

    node = DatasetRecorder()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()