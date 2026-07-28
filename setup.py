from setuptools import find_packages, setup
from glob import glob # собственный пакет
import os

package_name = 'conveyor_sim'

def package_files(directory):
    paths = []

    for (path, _, filenames) in os.walk(directory):
        if filenames:
            install_path = os.path.join(
                "share",
                package_name,
                path
            )

            file_list = [
                os.path.join(path, f)
                for f in filenames
            ]

            paths.append(
                (install_path, file_list)
            )

    return paths


setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            "share/" + package_name,
            ["package.xml"],
        ),
        (
            os.path.join("share", package_name, "launch"),
            glob("launch/*.py"),
        ),
    ]
    + package_files("worlds")
    + package_files("models")
    + package_files("config")
    + package_files("rviz"),
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="vvmanz",
    maintainer_email="vvmanz@todo.todo",
    description="Conveyor simulation with Gazebo Harmonic",
    license="Apache-2.0",
    extras_require={
        "test": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "simulation_manager = conveyor_sim.simulation_manager:main",
            "dataset_recorder = conveyor_sim.dataset_recorder:main",
            "sorter_controller = conveyor_sim.sorter_controller:main"
        ],
    },
)