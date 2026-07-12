from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    package_share = get_package_share_directory(
        "conveyor_sim"
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_share,
                "launch",
                "gazebo.launch.py",
            )
        )
    )
    bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_share,
                "launch",
                "bridge.launch.py",
            )
        )
    )
    nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_share,
                "launch",
                "nodes.launch.py",
            )
        )
    )
    return LaunchDescription([
        gazebo,
        bridge,
        nodes,
    ])