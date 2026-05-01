"""
Swarm Control - Main rover spawner and coordinator
Spawns 5-10 rovers with multimodal sensors in the Martian lava tube environment
"""

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Pose, PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan, Image, PointCloud2
from std_msgs.msg import String, Int32, Bool, Float32
from std_srvs.srv import Empty
import numpy as np
import transforms3d as t3d
import time
import yaml
import os


class Rover:
    """Individual rover representation"""
    def __init__(self, rover_id, pose, node):
        self.id = rover_id
        self.pose = pose
        self.node = node
        self.name = f"rover_{rover_id}"
        
        # Sensor data
        self.imu_data = None
        self.lidar_data = None
        self.vision_data = None
        
        # Communication status
        self.connected = True
        self.last_comm_time = time.time()
        
        # Local map fragment
        self.local_map = None
        self.local_map_timestamp = 0
        
        # SNN obstacle avoidance state
        self.snn_activations = np.zeros(8)  # 8 direction neurons
        self.avoidance_direction = 0
        
    def update_pose(self, pose):
        self.pose = pose
        
    def update_sensors(self, imu=None, lidar=None, vision=None):
        if imu: self.imu_data = imu
        if lidar: self.lidar_data = lidar
        if vision: self.vision_data = vision
        
    def set_communication_state(self, connected):
        self.connected = connected
        if connected:
            self.last_comm_time = time.time()
            
    def update_local_map(self, map_data):
        self.local_map = map_data
        self.local_map_timestamp = time.time()


class SwarmControl(Node):
    """Main swarm control node - spawns and coordinates rover swarm"""
    
    def __init__(self):
        super().__init__('swarm_control')
        
        # Parameters
        self.declare_parameter('num_rovers', 5)
        self.declare_parameter('spawn_area_x', 20.0)
        self.declare_parameter('spawn_area_y', 60.0)
        self.declare_parameter('comm_range', 15.0)
        self.declare_parameter('mesh_topology', 'dynamic')
        
        self.num_rovers = self.get_parameter('num_rovers').value
        self.spawn_area_x = self.get_parameter('spawn_area_x').value
        self.spawn_area_y = self.get_parameter('spawn_area_y').value
        self.comm_range = self.get_parameter('comm_range').value
        self.mesh_topology = self.get_parameter('mesh_topology').value
        
        # Rover fleet
        self.rovers = {}
        self.mesh_connections = {}  # {rover_id: [connected_rover_ids]}
        
        # Publishers
        self.swarm_status_pub = self.create_publisher(String, '/swarm/status', 10)
        self.map_fragment_pub = self.create_publisher(String, '/swarm/map_fragment', 10)
        self.comm_topology_pub = self.create_publisher(String, '/swarm/topology', 10)
        self.blackout_pub = self.create_publisher(Bool, '/swarm/blackout', 10)
        
        # Subscribers
        self.dust_sub = self.create_subscription(
            Float32, '/mars_environment/dust_intensity', self.dust_callback, 10)
        self.vision_blind_sub = self.create_subscription(
            Float32, '/mars_environment/vision_blinding', self.vision_blind_callback, 10)
        self.blackout_sub = self.create_subscription(
            Bool, '/chaos/blackout', self.blackout_callback, 10)
            
        # Services
        self.spawn_srv = self.create_service(
            Empty, '/swarm/spawn', self.spawn_callback)
        self.kill_srv = self.create_service(
            Empty, '/swarm/kill', self.kill_callback)
            
        # Initialize mesh topology
        self.init_mesh_topology()
        
        # Spawn initial rovers
        self.spawn_rovers()
        
        # Timers
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.mesh_timer = self.create_timer(1.0, self.mesh_update_callback)
        self.status_timer = self.create_timer(5.0, self.status_callback)
        
        self.get_logger().info(f'Swarm Control initialized with {self.num_rovers} rovers')
        
    def init_mesh_topology(self):
        """Initialize mesh network topology"""
        # Fully connected mesh by default
        for i in range(self.num_rovers):
            self.mesh_connections[i] = [j for j in range(self.num_rovers) if j != i]
            
    def spawn_rovers(self):
        """Spawn rovers in the Martian environment"""
        self.get_logger().info(f'Spawning {self.num_rovers} rovers...')
        
        for i in range(self.num_rovers):
            # Calculate spawn pose
            x = -self.spawn_area_x/2 + (i % 5) * (self.spawn_area_x / 4)
            y = -self.spawn_area_y/2 + (i // 5) * 10
            z = 0.0
            
            # Random orientation
            yaw = np.random.uniform(-np.pi, np.pi)
            
            pose = {'position': {'x': x, 'y': y, 'z': z}, 
                   'orientation': t3d.euler.euler2quat(0, 0, yaw)}
            
            # Create rover instance
            self.rovers[i] = Rover(i, pose, self)
            
            self.get_logger().info(f'Spawned rover_{i} at ({x:.1f}, {y:.1f})')
            
        self.publish_topology()
        
    def timer_callback(self):
        """Main control loop"""
        # Update each rover's state based on sensors
        for rover in self.rovers.values():
            self.update_rover_state(rover)
            
    def update_rover_state(self, rover):
        """Update individual rover state with SNN processing"""
        # Simulate sensor updates (in real system, would come from actual sensors)
        if rover.imu_data is None:
            rover.imu_data = {
                'linear_accel': np.random.randn(3) * 0.1,
                'angular_vel': np.random.randn(3) * 0.05,
                'orientation': rover.pose['orientation']
            }
            
        # Simulate LIDAR data (8 directions)
        if rover.lidar_data is None:
            # 360 degree scan with random obstacles
            distances = np.random.uniform(1.0, 10.0, 8)
            # Add some obstacles
            for j in range(3):
                idx = np.random.randint(0, 8)
                distances[idx] = np.random.uniform(0.5, 2.0)
            rover.lidar_data = distances
            
        # SNN-inspired obstacle detection
        rover.snn_activations = self.snn_process(rover.lidar_data)
        rover.avoidance_direction = np.argmax(rover.snn_activations)
        
    def snn_process(self, lidar_data):
        """Simple SNN-like processing for obstacle detection"""
        activations = np.zeros(8)
        
        for i, dist in enumerate(lidar_data):
            # Leaky Integrate-and-Fire model
            if dist < 2.0:
                activations[i] = 1.0 - (dist / 2.0)  # Strong activation near obstacles
            elif dist < 5.0:
                activations[i] = 0.3 * (1.0 - (dist - 2.0) / 3.0)  # Weaker activation
                
        return activations
        
    def mesh_update_callback(self):
        """Update mesh topology based on communication status"""
        # Check for broken links
        for rover in self.rovers.values():
            if not rover.connected:
                # Remove connections for disconnected rovers
                for other_id in list(self.mesh_connections.keys()):
                    if rover.id in self.mesh_connections[other_id]:
                        self.mesh_connections[other_id].remove(rover.id)
                        
        self.publish_topology()
        
    def publish_topology(self):
        """Publish current mesh topology"""
        msg = String()
        topology = {
            'connections': {str(k): v for k, v in self.mesh_connections.items()},
            'timestamp': time.time()
        }
        msg.data = yaml.dump(topology)
        self.comm_topology_pub.publish(msg)
        
    def status_callback(self):
        """Publish swarm status"""
        msg = String()
        status = {
            'num_rovers': self.num_rovers,
            'active_rovers': sum(1 for r in self.rovers.values() if r.connected),
            'mesh_links': sum(len(v) for v in self.mesh_connections.values()) // 2,
            'dust_level': getattr(self, 'current_dust', 0.0)
        }
        msg.data = yaml.dump(status)
        self.swarm_status_pub.publish(msg)
        
    def dust_callback(self, msg):
        """Handle dust storm intensity updates"""
        self.current_dust = msg.data
        
        # Blind vision sensors based on dust
        for rover in self.rovers.values():
            if rover.vision_data is None:
                rover.vision_data = {'visibility': 1.0}
            rover.vision_data['visibility'] = max(0, 1.0 - msg.data)
            
    def vision_blind_callback(self, msg):
        """Handle vision blinding updates"""
        for rover in self.rovers.values():
            if rover.vision_data is None:
                rover.vision_data = {'visibility': 1.0}
            rover.vision_data['visibility'] = max(0, 1.0 - msg.data)
            
    def blackout_callback(self, msg):
        """Handle blackout events from chaos monkey"""
        is_blackout = msg.data
        
        if is_blackout:
            self.get_logger().warn('BLACKOUT DETECTED - Switching to survival mode')
            # Sever all mesh connections
            for i in self.mesh_connections:
                self.mesh_connections[i] = []
            for rover in self.rovers.values():
                rover.set_communication_state(False)
        else:
            self.get_logger().info('BLACKOUT ENDED - Restoring mesh connections')
            self.init_mesh_topology()
            for rover in self.rovers.values():
                rover.set_communication_state(True)
                
        # Publish blackout state
        blackout_msg = Bool()
        blackout_msg.data = is_blackout
        self.blackout_pub.publish(blackout_msg)
        
    def spawn_callback(self, request, response):
        """Service to spawn additional rovers"""
        self.spawn_rovers()
        return response
        
    def kill_callback(self, request, response):
        """Service to kill all rovers"""
        self.rovers.clear()
        self.mesh_connections.clear()
        self.get_logger().info('All rovers terminated')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SwarmControl()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down swarm control')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
