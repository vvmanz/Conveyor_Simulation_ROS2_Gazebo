import rclpy
from ament_index_python.packages import get_package_share_directory
import os


from rclpy.node import Node

from .conveyor_controller import ConveyorController
from .sorter_hopper_controller import HopperController
from .tape_controller import TapeController
from .inclined_controller import InclinedConveyorsController

from .simulation_config import (
    CONVEYOR_SPEED,
    SPAWN_PERIOD,
    HOPPER_SPEED,
)
from .object_spawner import ObjectSpawner
from .spawn_registry import SpawnRegistry


class SimulationManager(Node):

    def __init__(self):
        super().__init__("simulation_manager")


        self.spawn_registry = SpawnRegistry()
        self.spawn_registry.clear()  

        self.conveyor = ConveyorController(self)
        self.tape = TapeController(self)
        self.inclined = InclinedConveyorsController(self)
        # self.hopper = HopperController(self)

        self.object_spawner = ObjectSpawner(self)

        self.get_logger().info("Simulation Manager started")

        self.conveyor.start(CONVEYOR_SPEED)
        self.tape.start(CONVEYOR_SPEED)

        self.inclined.set_speed_c(CONVEYOR_SPEED)
        self.inclined.set_speed_d(CONVEYOR_SPEED)

        # self.hopper.start(HOPPER_SPEED)

        self.spawn_timer = self.create_timer(
            SPAWN_PERIOD,
            self.spawn_random_object,
        )

        self.M = 7
        self.cleanup_timer = self.create_timer(
            1.0,
            lambda: self.spawn_registry.cleanup(self.M)
        )

        self.get_logger().info(
            f"Conveyor speed = {CONVEYOR_SPEED}"
        )
        # self.get_logger().info(
        #     f"Hopper speed = {CONVEYOR_SPEED}"
        # )

    def spawn_random_object(self):
        obj = self.object_spawner.spawn_random()
        if obj is None:
            return
        else:
            self.spawn_registry.add(obj)
        


def main():
    rclpy.init()
    node = SimulationManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()