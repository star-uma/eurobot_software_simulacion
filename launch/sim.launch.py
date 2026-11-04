import os
import tempfile
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_simulacion = get_package_share_directory('eurobot_software_simulacion')
    pkg_description = get_package_share_directory('eurobot_software_description')

    # Configuración de variables de entorno para recursos de Gazebo
    env_ign = AppendEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', os.path.join(pkg_simulacion, 'worlds'))
    env_gz = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(pkg_simulacion, 'worlds'))

    # ##########################################################
    # ##########################################################
    # FUSIÓN DINÁMICA DE PARÁMETROS (Fuente única de la verdad)
    # ##########################################################
    # ##########################################################

    params_robot_path = os.path.join(pkg_description, 'config', 'parametros_robot.yaml')
    with open(params_robot_path, 'r') as f:
        params_fisicos = yaml.safe_load(f)

    controllers_template_path = os.path.join(pkg_description, 'config', 'controllers.yaml')
    with open(controllers_template_path, 'r') as f:
        controllers_config = yaml.safe_load(f)

    # Inyección de medidas desde parametros_robot.yaml a controllers.yaml
    controllers_config['diff_cont']['ros__parameters']['wheel_separation'] = float(params_fisicos['wheel_separation'])
    controllers_config['diff_cont']['ros__parameters']['wheel_radius'] = float(params_fisicos['wheel_radius'])

    # Guardar en archivo temporal
    generated_controllers_path = os.path.join(tempfile.gettempdir(), 'eurobot_controllers_generado.yaml')
    with open(generated_controllers_path, 'w') as f:
        yaml.dump(controllers_config, f)

    # ##########################################################

    # 1. Lanza rsp.launch.py pasando el YAML generado y activando la simulación
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_description, 'launch', 'rsp.launch.py')]),
        launch_arguments={
            'use_sim_time': 'true',
            'use_sim': 'true',
            'controllers_yaml': generated_controllers_path
        }.items()
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
            '-x', '0.1',
            '-y', '1.0',
            '-z', '0.1', 
            '-Y', '0.0'
        ],
        output='screen'
    )

    # 4. Puente entre ROS 2 y Gazebo
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V' 
        ],
        output='screen'
    )

    # 5. Transformación estática provisional
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        output='screen'
    )

# 6. Spawner para el emisor de estados de las articulaciones (joint_broad)
    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
        output='screen'
    )

    # 7. Spawner para el controlador de tracción diferencial (diff_cont)
    diff_cont_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
        remappings=[('/diff_cont/cmd_vel_unstamped', '/cmd_vel')],
        output='screen'
    )

    return LaunchDescription([
        env_ign, 
        env_gz, 
        rsp, 
        gazebo, 
        spawn_entity, 
        bridge, 
        static_tf,
        joint_broad_spawner,
        diff_cont_spawner
    ])