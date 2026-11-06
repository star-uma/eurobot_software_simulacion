import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_desc = get_package_share_directory('eurobot_software_description')
    
    # Procesa el Xacro de prueba directamente
    xacro_file = os.path.join(pkg_desc, 'urdf', 'test.urdf.xacro')
    robot_description_xml = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description_xml, 'use_sim_time': True}]
        ),
        # Lanza Gazebo en un mundo vacío para ir rápido
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
            ]),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'test_robot']
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock']
        ),
        Node(package='controller_manager', executable='spawner', arguments=['joint_broad']),
        Node(package='controller_manager', executable='spawner', arguments=['test_cont']),
    ])