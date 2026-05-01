"""
Main launch file for Martian Swarm Quantum Simulation
Launches the complete multi-rover swarm system with all components
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnStartup
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description():
    # Launch arguments
    num_rovers_arg = DeclareLaunchArgument(
        'num_rovers',
        default_value='5',
        description='Number of rovers to spawn'
    )
    
    gazebo_world_arg = DeclareLaunchArgument(
        'gazebo_world',
        default_value='/workspace/gazebo_worlds/worlds/martian_lava_tube.world',
        description='Path to Gazebo world file'
    )
    
    enable_chaos_arg = DeclareLaunchArgument(
        'enable_chaos',
        default_value='true',
        description='Enable chaos monkey stress testing'
    )
    
    enable_quantum_arg = DeclareLaunchArgument(
        'enable_quantum',
        default_value='true',
        description='Enable quantum map merging'
    )
    
    # Environment setup
    set_env_vars = ExecuteProcess(
        cmd=['bash', '-c', 
             'export ROS_DOMAIN_ID=42 && '
             'export GAZEBO_MODEL_PATH=/workspace/gazebo_worlds/models:$GAZEBO_MODEL_PATH && '
             'export GAZEBO_RESOURCE_PATH=/workspace/gazebo_worlds/worlds:$GAZEBO_RESOURCE_PATH && '
             'echo "Environment configured"'],
        output='screen'
    )
    
    # Gazebo (if available)
    gazebo_node = ExecuteProcess(
        cmd=['gz', 'sim', LaunchConfiguration('gazebo_world')],
        output='screen',
        condition=None  # Can add condition to check if gazebo is available
    )
    
    # Swarm Control Node
    swarm_control_node = Node(
        package='swarm_control',
        executable='swarm_node.py',
        name='swarm_control',
        parameters=[{
            'num_rovers': LaunchConfiguration('num_rovers'),
            'spawn_area_x': 20.0,
            'spawn_area_y': 60.0,
            'comm_range': 15.0,
            'mesh_topology': 'dynamic'
        }],
        output='screen',
        emulate_tty=True
    )
    
    # SNN Controller Node (one per rover in real impl, simplified here)
    snn_controller_node = Node(
        package='snn_controller',
        executable='snn_node.py',
        name='snn_controller',
        parameters=[{
            'num_directions': 8,
            'threshold': 0.8,
            'max_speed': 0.5,
            'danger_threshold': 1.5
        }],
        output='screen'
    )
    
    # Chaos Monkey Node
    chaos_monkey_node = Node(
        package='chaos_monkey',
        executable='chaos_node.py',
        name='chaos_monkey',
        parameters=[{
            'num_rovers': LaunchConfiguration('num_rovers'),
            'blackout_probability': 0.001,
            'link_failure_prob': 0.01,
            'max_blackout_duration': 180.0,
            'min_blackout_duration': 30.0,
            'auto_trigger': LaunchConfiguration('enable_chaos')
        }],
        output='screen'
    )
    
    # Quantum Map Merge Node
    quantum_map_node = Node(
        package='quantum_map_merge',
        executable='quantum_node.py',
        name='quantum_map_merge',
        parameters=[{
            'use_quantum': LaunchConfiguration('enable_quantum'),
            'fragment_timeout': 60.0,
            'overlap_threshold': 0.3,
            'grid_resolution': 0.1
        }],
        output='screen'
    )
    
    # RViz for visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', '/workspace/ros2_ws/src/swarm_control/config/swarm.rviz'],
        condition=None
    )
    
    # Create launch description
    ld = LaunchDescription([
        num_rovers_arg,
        gazebo_world_arg,
        enable_chaos_arg,
        enable_quantum_arg,
        set_env_vars,
        swarm_control_node,
        snn_controller_node,
        chaos_monkey_node,
        quantum_map_node,
        # rviz_node  # Uncomment if RViz is available
    ])
    
    return ld
