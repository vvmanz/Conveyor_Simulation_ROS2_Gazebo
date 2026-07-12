from std_msgs.msg import Float64

class HopperController:
    def __init__(self, node):
        self._node = node
        self._publisher = node.create_publisher(
            Float64,
            "/hopper_speed",
            10
        )

        self._speed = 0.0

        # Публикуем 10 раз в секунду
        self._timer = node.create_timer(
            0.1,
            self._publish_speed
        )

    @property
    def speed(self):
        return self._speed

    def set_speed(self, speed: float):
        self._speed = speed
        self._node.get_logger().info(
            f"Sorter hopper speed -> {speed:.2f} m/s"
        )

    def _publish_speed(self):
        msg = Float64()
        msg.data = self._speed
        self._publisher.publish(msg)

    def stop(self):
        self.set_speed(0.0)

    def start(self, speed):
        self.set_speed(speed)