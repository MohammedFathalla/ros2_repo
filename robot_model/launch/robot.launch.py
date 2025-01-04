import os
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, FindExecutable , Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from math import radians
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    # Get the package containing the Ignition Gazebo launch file
    pkg_project_description = get_package_share_directory('robot_model')

    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Path to the ROS 2-Gazebo bridge parameters file
    bridge_params = os.path.join(
    get_package_share_directory('robot_model'),
    'config',
    'parameters.yaml'
    )
    
    urdf = os.path.join(pkg_project_description, 'urdf', 'my_robot.urdf')
    
    with open(urdf, 'r') as urdf_file:
        robot_description_content = urdf_file.read()
    

    # Publishes TF for links of the robot without joints
    robot_state = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{"robot_description": robot_description_content , 'use_sim_time' : True }]
        # parameters=[{'robot_description': robot_description_content}],
        # arguments=[urdf]
    )


    # RViz visualization
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d' , os.path.join(pkg_project_description, 'config', 'robot2.config.rviz')],
        output='screen'
    )

    spawn = Node(
    package='ros_gz_sim',
    executable='create',
    arguments=[
        '-name', "ros2_robot",
        '-topic', 'robot_description'
    ],
    output='screen'
    )
    
    # Setup to launch the simulator and Gazebo world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': PathJoinSubstitution([
            pkg_project_description,
            'world',
            'default.sdf'
        ])}.items()
    )
    
    
    bridge =  Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '--ros-args',
        '-p',
        f'config_file:={bridge_params}'
    ],
    output='screen'
)   

    
    return LaunchDescription([
        # ign_gazebo,
        gz_sim,
        robot_state,
        # joint_state,
        # image_bridge,
        spawn,
        bridge,
        rviz
    ])

