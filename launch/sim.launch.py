import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Obtenemos las rutas de AMBOS paquetes
    pkg_simulacion = get_package_share_directory('eurobot_software_simulacion')
    pkg_description = get_package_share_directory('eurobot_software_description')

    # La carpeta worlds se quedó en simulación
    env_ign = AppendEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', os.path.join(pkg_simulacion, 'worlds'))
    env_gz = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(pkg_simulacion, 'worlds'))

    # 1. Lanza rsp.launch.py desde el paquete description
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_description, 'launch', 'rsp.launch.py')]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 2. Lanza Gazebo cargando el archivo SDF desde simulación
    world_file = os.path.join(pkg_simulacion, 'worlds', 'eurobot.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': ['-r ', world_file]}.items()
    )

    # 3. Nodo que coge la descripción del robot y lo "spawnea" en Gazebo

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'eurobot',
            '-x', '0.1',   # Nuevo lateral izquierdo positivo
            '-y', '1.0',   # Nuevo centro vertical positivo
            '-z', '0.1', 
            '-Y', '0.0'
        ],
        output='screen'
    )


    # Estructura arguments
    # / topic_name @ configuración(paquete_al_hace_referncia) ("[" msg_hacia_ros2 "]" msg_hacia_ignition "@" bidireccional) estructura_interna_msg
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V' 
        ],
        output='screen'
    )

    # Incio en el mismo lugar que map y odom. Luego map se actualiza con el lidar de forma discreta y odom se actualiza con la odometría del robot
    # de forma continua. El sensor va corrigiendo los fallos de la odomtería. Nodo provisional hasta que se implemente el nodo de NAV2
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        output='screen'
    )

    return LaunchDescription([env_ign, env_gz, rsp, gazebo, spawn_entity, bridge, static_tf])

