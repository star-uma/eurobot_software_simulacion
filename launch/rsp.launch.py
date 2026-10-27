import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    # 1. Configuración del tiempo (Esencial para la transición a Gazebo)
    use_sim_time = LaunchConfiguration('use_sim_time')

    # 2. Localización dinámica de los archivos, usamos robot.urdf.xacro porque es el que contiene tanto el robot como los sensores
    pkg_path = get_package_share_directory('eurobot_software_simulacion')
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')

    # 3. Configuración del nodo principal
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(Command(['xacro ', xacro_file]), value_type=str),
            'use_sim_time': use_sim_time
        }]
    )

    # 4. Orquestación y ejecución
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',                                          # Cambiar a true si se quiere usar Gazebo
            description='Usar tiempo de simulación si es true (Gazebo)'
        ),
        node_robot_state_publisher
    ])
