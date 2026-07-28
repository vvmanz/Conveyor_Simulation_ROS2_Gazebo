import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.msgs10.entity_pb2 import Entity
from gz.msgs10.boolean_pb2 import Boolean

P_OPEN = 0.78
P_CLOSE = 0.0
HOLD_DELAY = 1      # Время N секунд для удержания заслонки после пересечения метки
LIFETIME_DELAY = 10.0   # Время M секунд жизни объекта С МОМЕНТА НАЗНАЧЕНИЯ КЛАССА

class ObjectSorterNode(Node):
    def __init__(self):
        super().__init__("object_sorter_node")

        self.tracked_objects = {}

        self.pub_pusher_1 = self.create_publisher(Float64, "/pusher_1", 10)
        self.pub_pusher_2 = self.create_publisher(Float64, "/pusher_2", 10)
   
        self.create_subscription(String, "/object_classification", self.classification_callback, 10)
   
        self.gz_node = GzNode()
        self.gz_node.subscribe(Pose_V, "/world/conveyor_world/dynamic_pose/info", self.pose_callback)
        self.get_logger().info("Система автоматической сортировки и жесткого удаления запущена.")

    def send_pusher_command(self, pusher_id, value):
        msg = Float64()
        msg.data = value
        if pusher_id == 1:
            self.pub_pusher_1.publish(msg)
            self.get_logger().info(f"⚙️ Заслонка 1 -> {value}")
        elif pusher_id == 2:
            self.pub_pusher_2.publish(msg)
            self.get_logger().info(f"⚙️ Заслонка 2 -> {value}")

    def remove_entity_gz(self, entity_name):
        """Прямой вызов сервиса Gazebo Transport для физического удаления модели"""
        req = Entity()
        req.name = entity_name
        req.type = 2  # MODEL
        
        service_name = "/world/conveyor_world/remove"
        
        success = self.gz_node.request(service_name, req, Entity, Boolean, 1000)
        if success:
            self.get_logger().error(f"🗑️ [Gazebo] Объект {entity_name} удален по истечении таймера жизни.")
        else:
            self.get_logger().error(f"❌ Не удалось отправить запрос на удаление объекта {entity_name} (возможно, уже удален)")

        if entity_name in self.tracked_objects:
            del self.tracked_objects[entity_name]

    def classification_callback(self, msg):
        try:
            data = json.loads(msg.data)
            obj_name = data.get("name")
            obj_class = data.get("class")
            
            if obj_name is None or obj_class is None:
                return
                
            if obj_name not in self.tracked_objects:
                self.tracked_objects[obj_name] = {
                    "class": obj_class,
                    "triggered": False
                }
                self.get_logger().info(f"📦 Новая посылка: {obj_name} [Класс {obj_class}]. Настройка пушеров...")
                
                if obj_class == 0:
                    self.send_pusher_command(1, P_CLOSE)
                    self.send_pusher_command(2, P_CLOSE)
                elif obj_class == 1:
                    self.send_pusher_command(1, P_OPEN)
                    self.send_pusher_command(2, P_CLOSE)
                elif obj_class == 2:
                    self.send_pusher_command(1, P_CLOSE)
                    self.send_pusher_command(2, P_OPEN)
                
                # Запускаем таймер удаления (имитируем oneshot через кастомный метод)
                timer = [None]
                timer[0] = self.create_timer(
                    LIFETIME_DELAY, 
                    lambda: self._oneshot_remove_callback(timer[0], obj_name)
                )
                    
        except json.JSONDecodeError:
            self.get_logger().error(f"Ошибка парсинга JSON: {msg.data}")

    def _oneshot_remove_callback(self, timer, obj_name):
        """Колбэк для таймера удаления, который сразу же отменяет сам себя"""
        if timer:
            timer.cancel()
            self.destroy_timer(timer)
        self.remove_entity_gz(obj_name)

    def pose_callback(self, msg):
        if not self.tracked_objects:
            return

        for pose in msg.pose:
            name = pose.name
            if name not in self.tracked_objects:
                continue
                
            obj_data = self.tracked_objects[name]
            
            if obj_data["triggered"]:
                continue
                
            current_y = pose.position.y
            obj_class = obj_data["class"]
            
            if obj_class == 1 and current_y <= 1.2:
                obj_data["triggered"] = True
                self.get_logger().info(f"{name} поравнялся с заслонкой 1 (y={current_y:.2f}м). Закрытие через {HOLD_DELAY}с...")
                
                timer = [None]
                timer[0] = self.create_timer(
                    HOLD_DELAY, 
                    lambda: self._oneshot_pusher_callback(timer[0], 1, name)
                )

            elif obj_class == 2 and current_y <= -0.4:
                obj_data["triggered"] = True
                self.get_logger().info(f"{name} поравнялся с заслонкой 2 (y={current_y:.2f}м). Закрытие через {HOLD_DELAY}с...")
                
                timer = [None]
                timer[0] = self.create_timer(
                    HOLD_DELAY, 
                    lambda: self._oneshot_pusher_callback(timer[0], 2, name)
                )

            elif obj_class == 0 and current_y <= -0.5: 
                obj_data["triggered"] = True
                if name in self.tracked_objects:
                    del self.tracked_objects[name]

    def _oneshot_pusher_callback(self, timer, pusher_id, object_name):
        """Колбэк для закрытия заслонки, который сразу же отменяет сам себя"""
        if timer:
            timer.cancel()
            self.destroy_timer(timer)
            
        self.get_logger().warn(f"Закрытие заслонки {pusher_id} после объекта {object_name}.")
        self.send_pusher_command(pusher_id, P_CLOSE)

        if object_name in self.tracked_objects:
            del self.tracked_objects[object_name]
            self.get_logger().info(f"➖ Объект {object_name} удален из памяти трекера.")

def main():
    rclpy.init()
    node = ObjectSorterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
