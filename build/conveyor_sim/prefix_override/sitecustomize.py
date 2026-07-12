import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/vvmanz/ros2_ws/src/conveyor_sim/install/conveyor_sim'
