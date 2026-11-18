# conveyor_sim

**Сортировочная конвейерная станция в Gazebo Harmonic и ROS 2: ленты, RGB-D камера, два толкателя, запись датасета и сортировщик, в который можно подключить свой классификатор.**

[English](README.md) | Русский

conveyor_sim — пакет ROS 2 (`ament_python`), имитирующий складскую сортировочную линию; сделан под логистический кейс
(Ozon Tech). Грузы разной формы и цвета падают на главную ленту, проезжают под RGB-D камерой, которая снимает каждую
посылку, получают класс (0, 1 или 2) и двумя толкателями направляются на нужную ветку линии. Вся станция — это
SDF-модели и несколько Python-узлов, общающихся через `ros_gz_bridge`, поэтому классификатор, логику лент и набор
грузов можно менять, не трогая физику.

```
 спавн ──► главная лента ──► RGB-D камера ──► класс 0 ──► оба толкателя закрыты, посылка остаётся на главной линии
                                  │               ├──► класс 1 ──► толкатель 1 ──► боковая ветка (наклонная лента C)
                                  ▼               └──► класс 2 ──► толкатель 2 ──► боковая ветка (наклонная лента D)
                        dataset_ozon/<объект>/
                          rgb/*.png  depth/*.npy
```

## Возможности

* **Станция целиком в SDF**: главная лента, лента зоны B, лента к сортировщику B, roll tape, две наклонные ленты (C, D),
  бункер сортировщика, два толкателя, две roll cage, камера с держателем (`models/environment/`, собрано в
  `worlds/conveyor_world.sdf`).
* **Библиотека грузов**: 8 STL-моделей (bottle, box1, box2, detergent, helmet, launchbox, pen, plate) и пуф. Каждому
  появившемуся объекту выдаётся случайный цвет из 7 (`models/cargo/`). Новая модель — это папка с `model.sdf`.
* **Спавнер и реестр**: `simulation_manager` каждые 2 с сбрасывает случайную посылку в начало ленты, ведёт
  JSON-реестр живых объектов и убирает за ними.
* **Запись датасета**: `dataset_recorder` сохраняет 3 RGB-кадра (PNG) и 3 кадра глубины (`.npy`) каждой посылки, пока она
  едет через зону камеры, в `dataset_ozon/<объект>/rgb|depth/`, и публикует результат классификации в
  `/object_classification` в виде JSON `{"name": ..., "class": 0|1|2}`.
* **Сортировщик**: `sorter_controller` открывает толкатель 1 для класса 1 и толкатель 2 для класса 2, закрывает его через
  секунду после прохода посылки, пропускает класс 0 прямо и удаляет каждый объект из мира через 10 с после
  классификации (прямой вызов сервиса Gazebo `/world/conveyor_world/remove`).
* **Интерфейс ROS 2** через `ros_gz_bridge`: скорости лент, команды толкателям и камера (таблица ниже).

> Классификатор — заглушка: после третьего кадра `dataset_recorder` выбирает случайный класс от 0 до 2. Замените это
> одно место своей моделью (достаточно публиковать тот же JSON в `/object_classification`), остальная линия
> работает без изменений.

### Топики

| топик | тип | направление | что |
|---|---|---|---|
| `/conveyor_speed`, `/conveyor_zone_b_speed`, `/to_sorter_b_speed`, `/tape_speed`, `/hopper_speed` | `std_msgs/Float64` | ROS → Gazebo | скорости лент |
| `/inclined_conveyor_speed_c`, `/inclined_conveyor_speed_d` | `std_msgs/Float64` | ROS → Gazebo | наклонные ленты |
| `/pusher_1`, `/pusher_2` | `std_msgs/Float64` | ROS → Gazebo | положение толкателя (0 — закрыт, 0.78 — открыт) |
| `/camera/image_raw`, `/camera/depth_raw`, `/camera/camera_info`, `/camera/points` | `sensor_msgs/Image`, `CameraInfo`, `PointCloud2` | Gazebo → ROS | RGB-D камера |
| `/object_classification` | `std_msgs/String` (JSON) | recorder → sorter | класс посылки |

## Требования

* Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic (gz-sim 8);
* `ros-jazzy-ros-gz` (`ros_gz_sim`, `ros_gz_bridge`), `ros-jazzy-cv-bridge`, `tf2_ros`;
* Python ≥ 3.10 с numpy, OpenCV и Python-биндингами Gazebo (`gz.transport13`, `gz.msgs10`).

## Установка

```bash
mkdir -p ~/conveyor_ws/src && cd ~/conveyor_ws/src
git clone https://github.com/<your-account>/conveyor_sim.git
cd ~/conveyor_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select conveyor_sim --symlink-install
source install/setup.bash
```

> Собирайте с `--symlink-install`: тогда датасет (`dataset_ozon/`) пишется в корень рабочего пространства, рядом с `src/`.

## Быстрый старт

```bash
ros2 launch conveyor_sim simulation.launch.py      # Gazebo + мост + все узлы
```

`simulation.launch.py` включает три launch-файла, которые можно запускать и по отдельности:

```bash
ros2 launch conveyor_sim gazebo.launch.py          # только мир
ros2 launch conveyor_sim bridge.launch.py          # только ros_gz_bridge
ros2 launch conveyor_sim nodes.launch.py           # simulation_manager, dataset_recorder, sorter_controller, static TF
```

Скорости лент и период появления посылок лежат в `conveyor_sim/simulation_config.py`; углы толкателей и тайминги
(`P_OPEN`, `HOLD_DELAY`, `LIFETIME_DELAY`) — в начале `conveyor_sim/sorter_controller.py`.

## Сделайте под себя

| хотите | делайте |
|---|---|
| подключить настоящий классификатор | публикуйте `{"name": "<объект>", "class": 0|1|2}` как `std_msgs/String` в `/object_classification` вместо случайного выбора в `dataset_recorder.py` |
| добавить тип груза | положите папку с `model.sdf`, `model.config` и мешем в `models/cargo/` и пересоберите: спавнер сканирует эту папку |
| изменить частоту посылок | `SPAWN_PERIOD` в `conveyor_sim/simulation_config.py` |
| изменить скорость ленты | `CONVEYOR_SPEED`, `HOPPER_SPEED` в том же файле |
| снимать больше кадров на посылку | `NUM_IMAGES`, `Y_MAX`, `Y_MIN` в `conveyor_sim/dataset_recorder.py` |

## Структура репозитория

```
conveyor_sim/      Python-узлы: simulation_manager, object_spawner, spawn_registry, dataset_recorder,
                   sorter_controller, контроллеры лент (conveyor, tape, inclined, zone B, to sorter B, hopper)
launch/            launch-файлы simulation, gazebo, bridge и nodes
models/cargo/      посылки (STL + SDF)
models/environment/ ленты, толкатели, roll cage, камера и держатель
worlds/            conveyor_world.sdf
```

## Лицензия

Apache-2.0, см. [`LICENSE`](LICENSE).
