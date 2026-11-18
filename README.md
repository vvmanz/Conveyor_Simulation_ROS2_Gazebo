# conveyor_sim

**A parcel-sorting conveyor station in Gazebo Harmonic and ROS 2: belts, an RGB-D camera, two pushers, a dataset recorder and a sorter you can plug your own classifier into.**

English | [Русский](README.ru.md)

conveyor_sim is a ROS 2 (`ament_python`) package that simulates a warehouse sorting line, built for a logistics case
(Ozon Tech). Cargo of different shapes and colours is dropped onto the main belt, rides under an RGB-D camera that
records images of every parcel, receives a class (0, 1 or 2) and is then routed by two pushers onto the matching branch
of the line. The whole station is plain SDF models plus a handful of Python nodes talking through `ros_gz_bridge`, so you
can replace the classifier, the belt logic or the cargo set without touching the physics.

```
 spawn ──► main belt ──► RGB-D camera ──► class 0 ──► both pushers closed, parcel stays on the main line
                              │               ├──► class 1 ──► pusher 1 ──► side branch (inclined belt C)
                              ▼               └──► class 2 ──► pusher 2 ──► side branch (inclined belt D)
                      dataset_ozon/<object>/
                        rgb/*.png  depth/*.npy
```

## Features

* **Complete station in SDF**: main belt, zone B belt, belt to sorter B, roll tape, two inclined belts (C, D), a sorter
  hopper, two pushers, two roll cages, the camera and its holder (`models/environment/`, assembled in
  `worlds/conveyor_world.sdf`).
* **Cargo library**: 8 STL models (bottle, box1, box2, detergent, helmet, launchbox, pen, plate) plus an ottoman. Every
  spawned object gets a random colour out of 7 (`models/cargo/`). Adding a model is one folder with `model.sdf`.
* **Spawner and registry**: `simulation_manager` drops a random parcel every 2 s at the top of the belt, keeps a JSON
  registry of live objects and cleans up after them.
* **Dataset recorder**: `dataset_recorder` saves 3 RGB frames (PNG) and 3 depth frames (`.npy`) of every parcel as it
  travels through the camera zone, into `dataset_ozon/<object>/rgb|depth/`, and publishes the result of classification
  on `/object_classification` as JSON `{"name": ..., "class": 0|1|2}`.
* **Sorter**: `sorter_controller` opens pusher 1 for class 1 and pusher 2 for class 2, closes it a second after the
  parcel passes, lets class 0 go straight through, and removes every object from the world 10 s after it was classified
  (a direct call to the Gazebo `/world/conveyor_world/remove` service).
* **ROS 2 interface** through `ros_gz_bridge`: belt speeds, pusher commands and the camera (see the table below).

> The classifier is a stub: `dataset_recorder` currently picks a random class from 0 to 2 after the third frame. Replace
> that one place with your model (it only needs to publish the same JSON on `/object_classification`) and the rest of the
> line works unchanged.

### Topics

| topic | type | direction | what |
|---|---|---|---|
| `/conveyor_speed`, `/conveyor_zone_b_speed`, `/to_sorter_b_speed`, `/tape_speed`, `/hopper_speed` | `std_msgs/Float64` | ROS → Gazebo | belt speeds |
| `/inclined_conveyor_speed_c`, `/inclined_conveyor_speed_d` | `std_msgs/Float64` | ROS → Gazebo | inclined belts |
| `/pusher_1`, `/pusher_2` | `std_msgs/Float64` | ROS → Gazebo | pusher position (0 closed, 0.78 open) |
| `/camera/image_raw`, `/camera/depth_raw`, `/camera/camera_info`, `/camera/points` | `sensor_msgs/Image`, `CameraInfo`, `PointCloud2` | Gazebo → ROS | RGB-D camera |
| `/object_classification` | `std_msgs/String` (JSON) | recorder → sorter | class of a parcel |

## Requirements

* Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic (gz-sim 8);
* `ros-jazzy-ros-gz` (`ros_gz_sim`, `ros_gz_bridge`), `ros-jazzy-cv-bridge`, `tf2_ros`;
* Python ≥ 3.10 with numpy, OpenCV and the Gazebo Python bindings (`gz.transport13`, `gz.msgs10`).

## Installation

```bash
mkdir -p ~/conveyor_ws/src && cd ~/conveyor_ws/src
git clone https://github.com/<your-account>/conveyor_sim.git
cd ~/conveyor_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select conveyor_sim --symlink-install
source install/setup.bash
```

> Build with `--symlink-install`: the dataset (`dataset_ozon/`) is then written to the workspace root, next to `src/`.

## Quick start

```bash
ros2 launch conveyor_sim simulation.launch.py      # Gazebo + bridge + all nodes
```

`simulation.launch.py` includes three launch files that can also be started on their own:

```bash
ros2 launch conveyor_sim gazebo.launch.py          # the world only
ros2 launch conveyor_sim bridge.launch.py          # ros_gz_bridge only
ros2 launch conveyor_sim nodes.launch.py           # simulation_manager, dataset_recorder, sorter_controller, static TF
```

Belt speeds and the spawn period live in `conveyor_sim/simulation_config.py`; pusher angles and timings
(`P_OPEN`, `HOLD_DELAY`, `LIFETIME_DELAY`) at the top of `conveyor_sim/sorter_controller.py`.

## Make it yours

| you want to | do |
|---|---|
| plug in a real classifier | publish `{"name": "<object>", "class": 0|1|2}` as `std_msgs/String` on `/object_classification` instead of the random choice in `dataset_recorder.py` |
| add a cargo type | put a folder with `model.sdf`, `model.config` and a mesh into `models/cargo/`, rebuild: the spawner scans the folder |
| change how fast parcels come | `SPAWN_PERIOD` in `conveyor_sim/simulation_config.py` |
| change belt speed | `CONVEYOR_SPEED`, `HOPPER_SPEED` in the same file |
| record more frames per parcel | `NUM_IMAGES`, `Y_MAX`, `Y_MIN` in `conveyor_sim/dataset_recorder.py` |

## Repository layout

```
conveyor_sim/      Python nodes: simulation_manager, object_spawner, spawn_registry, dataset_recorder,
                   sorter_controller, belt controllers (conveyor, tape, inclined, zone B, to sorter B, hopper)
launch/            simulation, gazebo, bridge and nodes launch files
models/cargo/      parcels (STL + SDF)
models/environment/ belts, pushers, roll cages, camera and holder
worlds/            conveyor_world.sdf
```

## Licence

Apache-2.0, see [`LICENSE`](LICENSE).
