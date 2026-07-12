from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    gz_sensor_path = "/world/conveyor_world/model/rgbd/link/camera_link/sensor/rgbd_sensor"

    bridge_topics = [
        "/conveyor_speed@std_msgs/msg/Float64]gz.msgs.Double",
        "/hopper_speed@std_msgs/msg/Float64]gz.msgs.Double",
        f"{gz_sensor_path}/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        f"{gz_sensor_path}/image@sensor_msgs/msg/Image[gz.msgs.Image",
        f"{gz_sensor_path}/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
        f"{gz_sensor_path}/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
    ]

    topic_remappings = [
        (f"{gz_sensor_path}/camera_info", "/camera/camera_info"),
        (f"{gz_sensor_path}/image", "/camera/image_raw"),
        (f"{gz_sensor_path}/depth_image", "/camera/depth_raw"),
        (f"{gz_sensor_path}/points", "/camera/points"),
    ]

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=bridge_topics,
        remappings=topic_remappings,
        output="screen",
    )

    return LaunchDescription([
        bridge,
    ])
