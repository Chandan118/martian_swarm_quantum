"""
Chaos Monkey - Swarm Resilience Testing Node
Randomly severs mesh communication to simulate radiation/storm interference
Forces rovers into decentralized bio-inspired survival mode
"""

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import Bool, String, Float32, Empty
from geometry_msgs.msg import PoseArray, Pose
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty as SrvEmpty
import numpy as np
import random
import time
import yaml
from collections import defaultdict


class ChaosMonkey(Node):
    """
    Chaos Monkey for Martian Swarm Testing
    
    This node simulates severe communication disruptions to test rover resilience:
    - Random mesh link severing (simulates radiation bursts)
    - Total blackout events (simulates dust storms blocking signals)
    - Gradual degradation (simulates antenna damage)
    
    During blackouts, rovers switch to survival mode:
    - Pure local sensor navigation
    - Ant-pheromone inspired collision avoidance
    - Energy conservation protocols
    """
    
    def __init__(self):
        super().__init__('chaos_monkey')
        
        # ROS Parameters
        self.declare_parameter('num_rovers', 5)
        self.declare_parameter('comm_range', 15.0)
        self.declare_parameter('blackout_probability', 0.001)  # per second
        self.declare_parameter('link_failure_prob', 0.01)      # per second per link
        self.declare_parameter('max_blackout_duration', 180.0)  # seconds
        self.declare_parameter('min_blackout_duration', 30.0)  # seconds
        self.declare_parameter('auto_trigger', True)
        self.declare_parameter('seed', None)
        
        self.num_rovers = self.get_parameter('num_rovers').value
        self.comm_range = self.get_parameter('comm_range').value
        self.blackout_probability = self.get_parameter('blackout_probability').value
        self.link_failure_prob = self.get_parameter('link_failure_prob').value
        self.max_blackout_duration = self.get_parameter('max_blackout_duration').value
        self.min_blackout_duration = self.get_parameter('min_blackout_duration').value
        self.auto_trigger = self.get_parameter('auto_trigger').value
        
        # Set random seed for reproducibility
        seed = self.get_parameter('seed').value
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # State tracking
        self.mesh_topology = {}  # Current mesh connections
        self.rover_positions = {}  # Rover positions for distance calculations
        self.active_blackout = False
        self.blackout_start_time = 0
        self.blackout_duration = 0
        self.survival_mode = False
        
        # Event tracking
        self.events = []
        self.total_blackouts = 0
        self.total_link_failures = 0
        
        # Publishers
        self.blackout_pub = self.create_publisher(Bool, '/chaos/blackout', 10)
        self.link_status_pub = self.create_publisher(String, '/chaos/link_status', 10)
        self.survival_mode_pub = self.create_publisher(Bool, '/chaos/survival_mode', 10)
        self.event_log_pub = self.create_publisher(String, '/chaos/event_log', 10)
        self.dust_intensity_pub = self.create_publisher(Float32, '/chaos/injected_dust', 10)
        
        # Subscribers
        self.swarm_status_sub = self.create_subscription(
            String, '/swarm/status', self.swarm_status_callback, 10)
        self.swarm_topology_sub = self.create_subscription(
            String, '/swarm/topology', self.topology_callback, 10)
        self.rover_odom_sub = self.create_subscription(
            Odometry, '/rover/odometry', self.odom_callback, 10)
            
        # Services (for manual control)
        self.trigger_blackout_srv = self.create_service(
            SrvEmpty, '/chaos/trigger_blackout', self.trigger_blackout)
        self.end_blackout_srv = self.create_service(
            SrvEmpty, '/chaos/end_blackout', self.end_blackout)
        self.get_status_srv = self.create_service(
            SrvEmpty, '/chaos/get_status', self.get_status)
            
        # Initialize mesh topology (fully connected)
        self.init_mesh()
        
        # Timers
        self.chaos_timer = self.create_timer(1.0, self.chaos_tick)  # Check every second
        self.status_timer = self.create_timer(5.0, self.publish_status)
        
        self.get_logger().info('Chaos Monkey initialized')
        self.get_logger().warn('WARNING: Chaos testing is ACTIVE')
        
    def init_mesh(self):
        """Initialize mesh network topology"""
        self.mesh_topology = defaultdict(set)
        for i in range(self.num_rovers):
            for j in range(i + 1, self.num_rovers):
                self.mesh_topology[i].add(j)
                self.mesh_topology[j].add(i)
                
        self.publish_link_status()
        self.log_event('INIT', 'Mesh network initialized - all links active')
        
    def chaos_tick(self):
        """
        Main chaos loop - check for random failures
        Called every second
        """
        if self.active_blackout:
            # Check if blackout should end
            elapsed = time.time() - self.blackout_start_time
            if elapsed >= self.blackout_duration:
                self.end_blackout_event()
            return
            
        # Check for random link failures
        self.check_link_failures()
        
        # Check for random blackout trigger
        if self.auto_trigger:
            if random.random() < self.blackout_probability:
                self.trigger_random_blackout()
                
    def check_link_failures(self):
        """Check each link for random failure"""
        failed_links = []
        
        for rover_a in list(self.mesh_topology.keys()):
            for rover_b in list(self.mesh_topology[rover_a]):
                # Random link failure
                if random.random() < self.link_failure_prob:
                    failed_links.append((rover_a, rover_b))
                    
        # Apply failures
        for a, b in failed_links:
            self.sever_link(a, b)
            
    def sever_link(self, rover_a, rover_b):
        """Sever a specific mesh link"""
        if b in self.mesh_topology[a]:
            self.mesh_topology[a].discard(b)
            self.mesh_topology[b].discard(a)
            self.total_link_failures += 1
            
            self.log_event('LINK_FAIL', f'Link severed: rover_{a} <-> rover_{b}')
            self.get_logger().warn(f'Link failure: rover_{a} <-> rover_{b}')
            
            # Check if rover is now isolated
            if len(self.mesh_topology[a]) == 0:
                self.log_event('ISOLATION', f'rover_{a} is now ISOLATED')
                self.get_logger().error(f'rover_{a} is completely isolated!')
                
            self.publish_link_status()
            
    def restore_link(self, rover_a, rover_b):
        """Restore a severed mesh link"""
        max_distance = self.comm_range * 1.5  # Allow slightly over nominal range
        
        # Check if rovers are close enough to reconnect
        if self.rover_is_in_range(rover_a, rover_b):
            self.mesh_topology[rover_a].add(rover_b)
            self.mesh_topology[rover_b].add(rover_a)
            
            self.log_event('LINK_RESTORE', f'Link restored: rover_{rover_a} <-> rover_{rover_b}')
            self.publish_link_status()
            return True
        return False
        
    def rover_is_in_range(self, rover_a, rover_b):
        """Check if two rovers are within communication range"""
        if rover_a not in self.rover_positions or rover_b not in self.rover_positions:
            return True  # Assume in range if no position data
            
        pos_a = self.rover_positions[rover_a]
        pos_b = self.rover_positions[rover_b]
        
        distance = np.sqrt(
            (pos_a[0] - pos_b[0])**2 + 
            (pos_a[1] - pos_b[1])**2
        )
        
        return distance <= self.comm_range
        
    def trigger_random_blackout(self):
        """Trigger a random blackout event"""
        duration = random.uniform(
            self.min_blackout_duration, 
            self.max_blackout_duration
        )
        
        # Choose blackout type
        blackout_type = random.choice(['gradual', 'instant', 'pulsing'])
        
        self.start_blackout(duration, blackout_type)
        
    def start_blackout(self, duration, blackout_type='instant'):
        """
        Start a communication blackout
        
        Args:
            duration: Blackout duration in seconds
            blackout_type: 'gradual', 'instant', or 'pulsing'
        """
        self.active_blackout = True
        self.blackout_start_time = time.time()
        self.blackout_duration = duration
        self.survival_mode = True
        self.total_blackouts += 1
        
        self.get_logger().warn('=' * 50)
        self.get_logger().warn(f'BLACKOUT STARTED - Type: {blackout_type}')
        self.get_logger().warn(f'Duration: {duration:.0f} seconds')
        self.get_logger().warn('=' * 50)
        
        if blackout_type == 'instant':
            # Immediately sever all links
            self.sever_all_links()
            
        elif blackout_type == 'gradual':
            # Gradually degrade links
            self.degrade_links_gradually()
            
        elif blackout_type == 'pulsing':
            # Intermittent connectivity
            self.start_pulsing_blackout()
            
        # Inject dust storm effect
        dust_msg = Float32()
        dust_msg.data = 0.8  # Heavy dust during blackout
        self.dust_intensity_pub.publish(dust_msg)
        
        # Publish blackout state
        msg = Bool()
        msg.data = True
        self.blackout_pub.publish(msg)
        
        survival_msg = Bool()
        survival_msg.data = True
        self.survival_mode_pub.publish(survival_msg)
        
        self.log_event('BLACKOUT_START', 
                       f'Type: {blackout_type}, Duration: {duration:.0f}s')
        
    def sever_all_links(self):
        """Sever all mesh connections"""
        self.mesh_topology = defaultdict(set)
        for i in range(self.num_rovers):
            self.mesh_topology[i] = set()  # Everyone isolated
            self.log_event('ISOLATION', f'rover_{i} is now ISOLATED')
            
        self.publish_link_status()
        
    def degrade_links_gradually(self):
        """Gradually degrade mesh links over time"""
        # First, sever 30% of links
        num_to_sever = int(len(self.mesh_topology) * 0.3)
        all_links = []
        
        for rover in self.mesh_topology:
            for connected in self.mesh_topology[rover]:
                all_links.append((rover, connected))
                
        links_to_sever = random.sample(all_links, min(num_to_sever, len(all_links)))
        
        for a, b in links_to_sever:
            self.sever_link(a, b)
            
        # Schedule remaining link failures
        # (In a full implementation, this would use additional timers)
        
    def start_pulsing_blackout(self):
        """Intermittent connectivity during blackout"""
        self.pulsing_state = True
        self.pulsing_timer = self.create_timer(10.0, self.pulse_callback)
        
    def pulse_callback(self):
        """Toggle connectivity during pulsing blackout"""
        if not self.active_blackout:
            if hasattr(self, 'pulsing_timer'):
                self.pulsing_timer.cancel()
            return
            
        if self.pulsing_state:
            # Turn off connectivity
            self.sever_all_links()
            self.log_event('PULSE', 'Pulsing blackout - links OFF')
        else:
            # Restore some connectivity (partial)
            self.restore_partial_links(0.3)  # 30% of links
            self.log_event('PULSE', 'Pulsing blackout - partial links ON')
            
        self.pulsing_state = not self.pulsing_state
        
    def restore_partial_links(self, fraction):
        """Restore a fraction of mesh links"""
        self.mesh_topology = defaultdict(set)
        
        for i in range(self.num_rovers):
            for j in range(i + 1, self.num_rovers):
                if random.random() < fraction:
                    if self.rover_is_in_range(i, j):
                        self.mesh_topology[i].add(j)
                        self.mesh_topology[j].add(i)
                        
        self.publish_link_status()
        
    def end_blackout_event(self):
        """End the current blackout and restore communications"""
        self.active_blackout = False
        self.survival_mode = False
        self.blackout_duration = 0
        
        # Cancel pulsing timer if active
        if hasattr(self, 'pulsing_timer'):
            self.pulsing_timer.cancel()
            
        # Gradually restore mesh connections
        self.restore_full_mesh()
        
        self.get_logger().info('=' * 50)
        self.get_logger().info('BLACKOUT ENDED - Communications restored')
        self.get_logger().info(f'Total blackouts this session: {self.total_blackouts}')
        self.get_logger().info('=' * 50)
        
        # Stop dust injection
        dust_msg = Float32()
        dust_msg.data = 0.0
        self.dust_intensity_pub.publish(dust_msg)
        
        # Publish blackout state
        msg = Bool()
        msg.data = False
        self.blackout_pub.publish(msg)
        
        survival_msg = Bool()
        survival_msg.data = False
        self.survival_mode_pub.publish(survival_msg)
        
        self.log_event('BLACKOUT_END', 'Communications restored')
        
    def restore_full_mesh(self):
        """Restore full mesh connectivity based on rover positions"""
        self.mesh_topology = defaultdict(set)
        
        for i in range(self.num_rovers):
            for j in range(i + 1, self.num_rovers):
                if self.rover_is_in_range(i, j):
                    self.mesh_topology[i].add(j)
                    self.mesh_topology[j].add(i)
                    
        self.publish_link_status()
        
        connected_count = sum(1 for r in self.mesh_topology if len(self.mesh_topology[r]) > 0)
        self.log_event('RESTORE', f'Full mesh restored - {connected_count}/{self.num_rovers} connected')
        
    def publish_link_status(self):
        """Publish current mesh link status"""
        msg = String()
        status = {
            'topology': {str(k): list(v) for k, v in self.mesh_topology.items()},
            'active_links': sum(len(v) for v in self.mesh_topology.values()) // 2,
            'isolated_rovers': sum(1 for r in self.mesh_topology if len(self.mesh_topology[r]) == 0),
            'blackout_active': self.active_blackout,
            'timestamp': time.time()
        }
        msg.data = yaml.dump(status)
        self.link_status_pub.publish(msg)
        
    def publish_status(self):
        """Publish chaos monkey status"""
        status = {
            'active_blackout': self.active_blackout,
            'total_blackouts': self.total_blackouts,
            'total_link_failures': self.total_link_failures,
            'survival_mode': self.survival_mode,
            'active_links': sum(len(v) for v in self.mesh_topology.values()) // 2,
            'isolated_rovers': sum(1 for r in self.mesh_topology if len(self.mesh_topology[r]) == 0)
        }
        
        if self.active_blackout:
            elapsed = time.time() - self.blackout_start_time
            remaining = self.blackout_duration - elapsed
            status['blackout_remaining'] = remaining
            
        self.get_logger().info(f'Status: {status}')
        
    def log_event(self, event_type, message):
        """Log a chaos event"""
        event = {
            'type': event_type,
            'message': message,
            'timestamp': time.time()
        }
        self.events.append(event)
        
        # Keep only recent events
        if len(self.events) > 1000:
            self.events = self.events[-500:]
            
        # Publish event
        msg = String()
        msg.data = yaml.dump(event)
        self.event_log_pub.publish(msg)
        
    # ROS Callbacks
    def swarm_status_callback(self, msg):
        """Handle swarm status updates"""
        pass  # Process if needed
        
    def topology_callback(self, msg):
        """Handle mesh topology updates from swarm"""
        try:
            data = yaml.safe_load(msg.data)
            if 'num_rovers' in data:
                self.num_rovers = data['num_rovers']
        except Exception as e:
            self.get_logger().debug(f'Topology parse error: {e}')
            
    def odom_callback(self, msg):
        """Handle rover odometry - track positions"""
        # Extract rover ID from frame (assuming frame name includes ID)
        frame = msg.header.frame_id
        if 'rover' in frame:
            try:
                rover_id = int(frame.split('_')[-1])
                self.rover_positions[rover_id] = [
                    msg.pose.pose.position.x,
                    msg.pose.pose.position.y
                ]
            except Exception as e:
                self.get_logger().debug(f'Odom parse error: {e}')
                
    # Service Handlers
    def trigger_blackout(self, request, response):
        """Manually trigger a blackout"""
        self.start_blackout(120, 'instant')
        return response
        
    def end_blackout(self, request, response):
        """Manually end the current blackout"""
        self.end_blackout_event()
        return response
        
    def get_status(self, request, response):
        """Get chaos monkey status"""
        status = {
            'active_blackout': self.active_blackout,
            'total_blackouts': self.total_blackouts,
            'total_link_failures': self.total_link_failures,
            'survival_mode': self.survival_mode,
            'events': self.events[-10:]  # Last 10 events
        }
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ChaosMonkey()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Chaos Monkey')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
