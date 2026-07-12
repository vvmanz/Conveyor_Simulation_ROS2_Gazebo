from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

from launch.actions import SetEnvironmentVariable
from launch.substitutions import EnvironmentVariable

import os


def generate_launch_description():
    package_share = get_package_share_directory("conveyor_sim")
    models_path = os.path.join(package_share, "models")

    cargo_models = os.path.join(
        package_share,
        "models",
        "cargo",
    )

    environment_models = os.path.join(
        package_share,
        "models",
        "environment",
    )

    set_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[
            cargo_models,
            ":",
            environment_models,
            ":",
            EnvironmentVariable(
                "GZ_SIM_RESOURCE_PATH",
                default_value=""
            )
        ]
    )

    world = os.path.join(
        package_share,
        "worlds",
        "conveyor_world.sdf"
    )
    gz_launch = os.path.join(
        get_package_share_directory("ros_gz_sim"),
        "launch",
        "gz_sim.launch.py"
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch),
        launch_arguments={
            "gz_args": f"-r {world}"
        }.items(),
    )
    return LaunchDescription([
        set_resource_path,
        gazebo,
    ])
