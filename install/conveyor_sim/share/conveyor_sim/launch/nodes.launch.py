from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    simulation_manager = Node(
        package="conveyor_sim",
        executable="simulation_manager",
        output="screen",
    )

    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "0", "0", "0",
            "0", "0", "0",
            "world",
            "rgbd/camera_link/rgbd_sensor",
        ],
        output="screen",
    )

    dataset_recoder = Node(
        package="conveyor_sim",
        executable="dataset_recorder",
        output="screen",
    ),

    return LaunchDescription([
        simulation_manager,
        static_tf,
        dataset_recoder,
    ])