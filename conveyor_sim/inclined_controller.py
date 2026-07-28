from std_msgs.msg import Float64

class InclinedConveyorsController:
    def __init__(self, node):
        self._node = node

        # 1. Объявляем параметры внутри родительской ноды
        self._node.declare_parameter("topic_c", "/inclined_conveyor_speed_c")
        self._node.declare_parameter("topic_d", "/inclined_conveyor_speed_d")
        self._node.declare_parameter("speed_c", 0.5)  # Дефолтная скорость 0.5 м/с
        self._node.declare_parameter("speed_d", 0.5)

        # 2. Читаем значения параметров (они подтянутся, если переданы в лаунче)
        self.topic_c = self._node.get_parameter("topic_c").get_parameter_value().string_value
        self.topic_d = self._node.get_parameter("topic_d").get_parameter_value().string_value
        self.speed_c = self._node.get_parameter("speed_c").get_parameter_value().double_value
        self.speed_d = self._node.get_parameter("speed_d").get_parameter_value().double_value

        # 3. Создаем паблишеры
        self._pub_c = self._node.create_publisher(Float64, self.topic_c, 10)
        self._pub_d = self._node.create_publisher(Float64, self.topic_d, 10)

        # 4. Запускаем один общий таймер публикации на частоте 10 Гц
        self._timer = self._node.create_timer(0.1, self._publish_speeds)

        self._node.get_logger().info(
            f"Inclined Controller initialized. C: {self.topic_c} ({self.speed_c} m/s), D: {self.topic_d} ({self.speed_d} m/s)"
        )

    def _publish_speeds(self):
        msg_c = Float64()
        msg_c.data = self.speed_c
        self._pub_c.publish(msg_c)

        msg_d = Float64()
        msg_d.data = self.speed_d
        self._pub_d.publish(msg_d)

    def set_speed_c(self, speed: float):
        self.speed_c = speed
        self._node.get_logger().info(f"Inclined C speed updated -> {speed:.2f} m/s")

    def set_speed_d(self, speed: float):
        self.speed_d = speed
        self._node.get_logger().info(f"Inclined D speed updated -> {speed:.2f} m/s")

    def stop(self):
        self.set_speed_c(0.0)
        self.set_speed_d(0.0)
