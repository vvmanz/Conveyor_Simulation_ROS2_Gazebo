#!/usr/bin/env python3

import rclpy

from rclpy.node import Node

from .conveyor_controller import ConveyorController
from .sorter_hopper_controller import HopperController

from .simulation_config import (
    CONVEYOR_SPEED,
    SPAWN_PERIOD,
    HOPPER_SPEED,
)
from .object_spawner import ObjectSpawner
from .pose import Pose
from .spawn_object import SpawnObject




class SimulationManager(Node):

    def __init__(self):
        super().__init__("simulation_manager")
        self.conveyor = ConveyorController(self)
        self.hopper = HopperController(self)

        self.object_spawner = ObjectSpawner(self)

        self.get_logger().info("Simulation Manager started")

        self.conveyor.start(CONVEYOR_SPEED)
        self.hopper.start(HOPPER_SPEED)

        self.spawn_timer = self.create_timer(
            SPAWN_PERIOD,
            self.spawn_random_object,
        )

        self.get_logger().info(
            f"Conveyor speed = {CONVEYOR_SPEED}"
        )
        self.get_logger().info(
            f"Hopper speed = {CONVEYOR_SPEED}"
        )

    def spawn_random_object(self):
        obj = self.object_spawner.spawn_random()
        if obj is None:
            return
        


def main():
    rclpy.init()
    node = SimulationManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()