import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Start headless Gazebo
    world_file_path = '/workspaces/okmr_sim/worlds/auv.sdf'

    gazebo_process = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', '-v', '4', world_file_path],
        additional_env={
            'DISPLAY': '',
            'LIBGL_ALWAYS_SOFTWARE': '1',
            'QT_QPA_PLATFORM': 'offscreen'
        },
        output='screen'
    )

    # ROS Gz parameter bridge
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cascade/fro@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/flo@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/bro@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/blo@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/fri@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/fli@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/bri@std_msgs/msg/Float64@gz.msgs.Double',
            '/cascade/bli@std_msgs/msg/Float64@gz.msgs.Double',
            '/model/cascade/odometry_with_covariance@nav_msgs/msg/Odometry@gz.msgs.OdometryWithCovariance'
        ],
        output='screen'
    )

    # Foxglove websocket bridge
    foxglove_bridge = IncludeLaunchDescription(
        AnyLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('foxglove_bridge'),
                'launch',
                'foxglove_bridge_launch.xml'
            )
        ]),
        launch_arguments={'port': '8765'}.items()
    )

    # 3D space visualization in Foxglove
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'underwater_world'],
        output='screen'
    )

    #Custom PID controller
    pid_controller = Node(
        package='okmr_control',
        executable='thruster_driver',
        output='screen'
    )

    return LaunchDescription([
        gazebo_process,
        ros_gz_bridge,
        foxglove_bridge,
        static_tf,
        pid_controller
    ])