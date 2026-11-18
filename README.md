# conveyor_sim

**A ROS 2 + Gazebo Harmonic simulation of an automated parcel-sorting conveyor, with RGB-D data collection and diverter control.**

English | [Русский](README.ru.md)

`conveyor_sim` is a simulation prototype of a warehouse sorting line. Gazebo handles the conveyor world and moving packages; ROS 2 coordinates spawning, camera acquisition, class messages and sorting actuators. The project also records paired RGB and depth samples for further computer-vision experiments.

## Features

- **Conveyor station** assembled from SDF models: belts, ramps, hoppers, diverters and cargo objects.
- **Automatic parcel generation** with randomly selected models, colors and initial orientations.
- **RGB-D recording**: three RGB frames (`.png`) and depth arrays (`.npy`) captured for each tracked object at defined positions.
- **Sorting scenario**: three classes (0, 1, 2), with two pusher actuators controlled according to the received class and object position.
- **ROS–Gazebo bridge** for conveyor commands and camera topics.

> **Scope:** the current `dataset_recorder.py` uses a **random class label** as a placeholder after collecting images. This is a demonstration of the sorting pipeline, **not a trained visual classifier**.

## Requirements

- Linux with ROS 2 and Gazebo Harmonic (`gz-sim 8`) and the matching `ros_gz_sim` / `ros_gz_bridge` packages.
- ROS 2 packages: `rclpy`, `sensor_msgs`, `std_msgs`, `tf2_ros`, `cv_bridge`.
- Python packages: `numpy`, `opencv-python` (or system-provided OpenCV).
- Python Gazebo Transport bindings used by the source: `gz.transport13`, `gz.msgs10`.
- `colcon` and a sourced ROS 2 environment.

The dependencies are inferred from the source and are **not packaged as a lockfile**. Check that the Python Gazebo bindings match the installed Gazebo distribution.

## Build and run

Place this repository in the `src/` directory of a ROS 2 workspace. Replace `YOUR_REPOSITORY_URL` with the actual clone URL and change `jazzy` if a different ROS 2 distro is installed:

```bash
mkdir -p ~/conveyor_ws/src
cd ~/conveyor_ws/src
git clone YOUR_REPOSITORY_URL conveyor_sim
cd ~/conveyor_ws
source /opt/ros/jazzy/setup.bash  # change if you use another ROS 2 distro
colcon build --symlink-install --packages-select conveyor_sim
source install/setup.bash
ros2 launch conveyor_sim simulation.launch.py
```

The launch file starts the Gazebo world, ROS–Gazebo bridge, simulation manager, dataset recorder, sorting controller and a static camera transform. Use a matching ROS 2 / Gazebo setup; this archive does not contain an automated environment installer.

## Architecture

```text
Gazebo Harmonic                 ROS 2
conveyor_world.sdf              simulation_manager
  ├─ conveyor models  <------  object spawn / cleanup
  ├─ moving parcels    ------>  object positions
  ├─ RGB-D camera      ------>  dataset_recorder
  └─ pusher actuators <------  sorter_controller
                                   ^
                                   └── /object_classification (JSON String)
```

**Useful topics**

| Topic | Purpose |
|---|---|
| `/camera/image_raw` | RGB camera image |
| `/camera/depth_raw` | Depth image |
| `/object_classification` | `{"name": "example_000001", "class": 1}` (classes: 0, 1, 2) as `std_msgs/String` |
| `/pusher_1`, `/pusher_2` | Pusher control bridged to Gazebo |

## Recorded data

`dataset_recorder.py` creates a `dataset_ozon/` directory relative to its resolved workspace path. Each object receives a folder with `rgb/000.png`–`002.png` and `depth/000.npy`–`002.npy`. Output paths depend on where the ROS package is installed and should be checked before a long run.

## Repository layout

```text
conveyor_sim/          ROS 2 nodes: manager, recorder, sorter, spawner and helpers
launch/                combined launch, Gazebo, bridge and nodes
models/cargo/          SDF parcel models
models/environment/    conveyor and station models
worlds/                conveyor_world.sdf
package.xml            ROS 2 package metadata
setup.py               ament_python package and console entry points
```

## Development notes

- This is an **integration/simulation prototype**, not a production sorting installation.
- The repository snapshot contains generated `build/`, `install/` and `log/` directories; in a clean checkout, rebuild locally.
- `package.xml` currently spells `rclpy` as `rlcpy` in an execution dependency. Correct that package manifest entry if dependency resolution fails.
- The included [`LICENSE`](LICENSE) is Apache-2.0.
