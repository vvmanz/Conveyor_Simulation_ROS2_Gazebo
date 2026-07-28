import json
import cv2
import numpy as np
from cv_bridge import CvBridge
import random
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import Int32, String
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent
JSON_PATH = PACKAGE_DIR / "spawned_objects.json"
WORKSPACE = Path(__file__).resolve().parents[3]
DATASET_DIR = WORKSPACE / "dataset_ozon"
Y_MAX = 2.50
Y_MIN = 1.60
NUM_IMAGES = 3
class DatasetRecorder(Node):
    def __init__(self):
        super().__init__("dataset_recorder")
        self.bridge = CvBridge()
        self.rgb_image = None
        self.depth_image = None
        self.tracked = {}
        self.capture_index = {}
        self.capture_points = np.linspace(Y_MAX, Y_MIN, NUM_IMAGES)
        # Паблишер для симуляции классификатора
        self.class_pub = self.create_publisher(String, "/object_classification", 10)

        self.gz_node = GzNode()
        self.gz_node.subscribe(
            Pose_V,
            "/world/conveyor_world/dynamic_pose/info",
            self.pose_callback,
        )

        self.create_subscription(Image, "/camera/image_raw", self.rgb_callback, qos_profile_sensor_data)
        self.create_subscription(Image, "/camera/depth_raw", self.depth_callback, qos_profile_sensor_data)
        self.create_timer(1.0, self.load_registry)

        self.get_logger().info("Dataset recorder started.")
        self.get_logger().info(f"Capture positions: {self.capture_points}")

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
        self.rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

    def depth_callback(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")

    def pose_callback(self, msg):
        if self.rgb_image is None or self.depth_image is None:
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
            cv2.imwrite(str(rgb_dir / f"{index:03d}.png"), self.rgb_image)
            np.save(depth_dir / f"{index:03d}.npy", self.depth_image)
            self.get_logger().info(f"{name}: saved {index+1}/{NUM_IMAGES}  y={y:.3f}")

            if index == NUM_IMAGES - 1: 
                predicted_class = random.randint(0, 2)                
               
                class_msg = Int32()
                class_msg.data = predicted_class                
                # Но лучше передавать имя + класс. Для простоты отправим строку через String или кастомное сообщение.
                # Чтобы не менять типы данных кардинально, используем строку JSON:
                # Но раз вы просили "число от 0 до 2, которое является сигналом", то сделаем структуру:
                # Передадим это в новый скрипт. Чтобы он знал имя объекта, используем топик классификации:
                
            self.capture_index[name] += 1

            if self.capture_index[name] == NUM_IMAGES:
                self.get_logger().info(f"{name}: capture complete. Class: {predicted_class}")
                
                # Отправляем событие классификации (Класс + Имя объекта через JSON-строку для точности слежения)
                from std_msgs.msg import String
                payload = json.dumps({"name": name, "class": predicted_class})
                msg_str = String()
                msg_str.data = payload
                # Объявим этот паблишер в __init__: self.class_pub = self.create_publisher(String, "/object_classification", 10)
                self.class_pub.publish(msg_str)


def main():
    rclpy.init()
    node = DatasetRecorder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
