"""
SNN Controller - Spiking Neural Network for Neuromorphic Obstacle Avoidance
Implements Leaky Integrate-and-Fire neurons optimized for M2 Mac

This controller mimics low-power, high-efficiency neuromorphic navigation
using bio-inspired spiking neural networks.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Bool, Int32
import numpy as np
import time


class SpikingNeuron:
    """
    Leaky Integrate-and-Fire (LIF) Spiking Neuron Model
    
    Membrane potential dynamics:
    tau * dV/dt = -V + I
    
    Spike generation when V >= V_threshold
    """
    
    def __init__(self, threshold=1.0, tau=10.0, reset_voltage=-0.1):
        self.V = 0.0  # Membrane potential
        self.threshold = threshold
        self.tau = tau  # Membrane time constant
        self.reset_voltage = reset_voltage
        self.spike_history = []
        self.last_spike_time = 0
        
    def update(self, input_current, dt=0.01):
        """
        Update neuron state
        
        Args:
            input_current: Synaptic input current
            dt: Time step in seconds
            
        Returns:
            spike: Boolean indicating if neuron spiked
        """
        # Leaky integration
        dV = (-self.V + input_current) / self.tau
        self.V += dV * dt
        
        # Check for spike
        spike = False
        if self.V >= self.threshold:
            spike = True
            self.spike_history.append(time.time())
            self.V = self.reset_voltage
            self.last_spike_time = time.time()
            
        return spike
    
    def get_firing_rate(self, window=1.0):
        """Calculate firing rate over time window"""
        if len(self.spike_history) < 2:
            return 0.0
            
        recent_spikes = [t for t in self.spike_history if time.time() - t <= window]
        if len(recent_spikes) < 2:
            return 0.0
            
        return len(recent_spikes) / window


class SNNLayer:
    """
    Layer of spiking neurons with lateral inhibition
    """
    
    def __init__(self, num_neurons, threshold=1.0, tau=10.0):
        self.neurons = [
            SpikingNeuron(threshold=threshold, tau=tau) 
            for _ in range(num_neurons)
        ]
        self.num_neurons = num_neurons
        self.weights = np.eye(num_neurons)  # Synaptic weights
        
        # Lateral inhibition matrix (winner-take-all)
        self.inhibition_strength = 0.8
        
    def set_input_weights(self, weights):
        """Set input synaptic weights"""
        if weights.shape == (self.num_neurons, len(weights)):
            self.weights = weights
            
    def propagate(self, inputs, dt=0.01):
        """
        Propagate inputs through the SNN layer
        
        Args:
            inputs: Input currents for each neuron
            dt: Time step
            
        Returns:
            spikes: Boolean array of spike outputs
        """
        spikes = np.zeros(self.num_neurons)
        
        for i, neuron in enumerate(self.neurons):
            # Calculate input current with lateral connections
            total_input = inputs[i]
            
            # Add lateral excitation/inhibition from other neurons
            for j in range(self.num_neurons):
                if i != j:
                    if self.weights[i, j] > 0:
                        total_input += self.weights[i, j] * inputs[j] * 0.1
                    else:
                        total_input += self.weights[i, j] * neuron.V * self.inhibition_strength
            
            # Update neuron
            spikes[i] = neuron.update(total_input, dt)
            
        # Apply lateral inhibition (winner-take-all)
        if np.any(spikes):
            winner = np.argmax(spikes)
            spikes = np.zeros(self.num_neurons)
            spikes[winner] = 1.0
            
        return spikes


class SNNController(Node):
    """
    SNN-based Obstacle Avoidance Controller
    
    Architecture:
    - Input Layer: 8 direction sensors (LiDAR)
    - Hidden Layer: 16 spiking neurons (feature extraction)
    - Output Layer: 8 motor commands (direction selection)
    
    This bio-inspired approach provides:
    - Low power consumption (sparse spiking)
    - Fast response (single spike propagation)
    - Robustness to noise (temporal coding)
    """
    
    def __init__(self):
        super().__init__('snn_controller')
        
        # ROS parameters
        self.declare_parameter('num_directions', 8)
        self.declare_parameter('threshold', 0.8)
        self.declare_parameter('max_speed', 0.5)
        self.declare_parameter('turn_speed', 0.8)
        self.declare_parameter('danger_threshold', 1.5)  # meters
        self.declare_parameter('window_size', 0.1)  # seconds
        
        self.num_directions = self.get_parameter('num_directions').value
        self.threshold = self.get_parameter('threshold').value
        self.max_speed = self.get_parameter('max_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value
        self.danger_threshold = self.get_parameter('danger_threshold').value
        
        # SNN Layers
        self.input_layer = SNNLayer(self.num_directions, threshold=0.5, tau=5.0)
        self.hidden_layer = SNNLayer(16, threshold=self.threshold, tau=10.0)
        self.output_layer = SNNLayer(self.num_directions, threshold=0.6, tau=8.0)
        
        # Input weights (sensor to input neurons)
        self.sensor_weights = np.random.randn(self.num_directions, self.num_directions) * 0.3
        self.input_layer.set_input_weights(self.sensor_weights)
        
        # State variables
        self.lidar_data = np.zeros(self.num_directions)
        self.current_command = Twist()
        self.last_update_time = time.time()
        
        # Statistics
        self.spike_counts = {'input': 0, 'hidden': 0, 'output': 0}
        self.total_updates = 0
        
        # Publishers
        self.cmd_pub = self.create_publisher(Twist, '/snn/cmd_vel', 10)
        self.activity_pub = self.create_publisher(Float32, '/snn/total_activity', 10)
        self.avoidance_pub = self.create_publisher(Int32, '/snn/avoidance_direction', 10)
        self.spike_pub = self.create_publisher(Bool, '/snn/spike_detected', 10)
        
        # Subscribers
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.blackout_sub = self.create_subscription(
            Bool, '/swarm/blackout', self.blackout_callback, 10)
            
        # Timer for continuous processing
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz
        
        self.get_logger().info('SNN Controller initialized')
        self.get_logger().info(f'Architecture: {self.num_directions} -> 16 -> {self.num_directions}')
        
    def scan_callback(self, msg):
        """Process LiDAR scan data"""
        # Convert LaserScan to direction-based input
        ranges = np.array(msg.ranges)
        
        # Handle inf values (no obstacle detected)
        ranges = np.where(np.isinf(ranges), msg.range_max, ranges)
        
        # Quantize to 8 directions
        num_readings = len(ranges)
        readings_per_direction = num_readings // self.num_directions
        
        direction_distances = []
        for i in range(self.num_directions):
            start_idx = i * readings_per_direction
            end_idx = (i + 1) * readings_per_direction
            # Use minimum distance in each sector (most dangerous)
            min_dist = np.min(ranges[start_idx:end_idx])
            direction_distances.append(min_dist)
            
        self.lidar_data = np.array(direction_distances)
        
    def blackout_callback(self, msg):
        """Handle communication blackout - intensify local processing"""
        if msg.data:
            self.get_logger().warn('BLACKOUT MODE - Relying purely on local sensors')
            # Increase sensitivity during blackout
            self.threshold *= 0.8
            
    def timer_callback(self):
        """Main SNN processing loop"""
        dt = time.time() - self.last_update_time
        self.last_update_time = time.time()
        
        if np.any(self.lidar_data):
            # Convert LiDAR distances to neural inputs
            # Closer obstacles = stronger input (danger signal)
            inputs = self.normalize_inputs(self.lidar_data)
            
            # Propagate through SNN
            input_spikes = self.input_layer.propagate(inputs, dt)
            hidden_spikes = self.hidden_layer.propagate(
                np.concatenate([input_spikes, np.zeros(8)]), dt)
            output_spikes = self.output_layer.propagate(
                hidden_spikes[:self.num_directions], dt)
            
            # Generate motor command from output spikes
            self.generate_command(output_spikes)
            
            # Update statistics
            self.spike_counts['input'] += np.sum(input_spikes)
            self.spike_counts['hidden'] += np.sum(hidden_spikes)
            self.spike_counts['output'] += np.sum(output_spikes)
            self.total_updates += 1
            
            # Publish activity
            total_activity = (np.sum(input_spikes) + np.sum(hidden_spikes) + 
                            np.sum(output_spikes)) / (self.num_directions + 16 + self.num_directions)
            self.activity_pub.publish(Float32(data=total_activity))
            
            # Publish avoidance direction
            if np.any(output_spikes):
                direction = np.argmax(output_spikes)
                self.avoidance_pub.publish(Int32(data=direction))
                
            # Publish spike activity
            has_spike = bool(np.any(input_spikes) or np.any(hidden_spikes) or np.any(output_spikes))
            self.spike_pub.publish(Bool(data=has_spike))
            
    def normalize_inputs(self, distances):
        """Convert distances to normalized input currents"""
        # Inverse relationship: closer = stronger input
        max_range = 10.0
        normalized = np.clip((max_range - distances) / max_range, 0, 1)
        
        # Scale and add noise for robustness
        inputs = normalized * 1.5 + np.random.randn(len(normalized)) * 0.05
        
        return inputs
        
    def generate_command(self, output_spikes):
        """Generate velocity command from SNN output"""
        cmd = Twist()
        
        if np.any(output_spikes):
            # Winner-take-all: use the most active direction
            winner = np.argmax(output_spikes)
            
            # Calculate direction (0 = forward, increasing clockwise)
            danger_detected = self.lidar_data[winner] < self.danger_threshold
            
            if danger_detected:
                # Emergency avoidance
                # Determine best escape direction
                safe_directions = np.where(self.lidar_data > self.danger_threshold)[0]
                
                if len(safe_directions) > 0:
                    # Pick the safest direction
                    best_idx = safe_directions[np.argmax(self.lidar_data[safe_directions])]
                    cmd = self.direction_to_cmd(best_idx)
                else:
                    # All directions blocked - backup
                    cmd.linear.x = -self.max_speed * 0.5
                    cmd.angular.z = self.turn_speed
            else:
                # Normal navigation
                cmd = self.direction_to_cmd(winner)
        else:
            # No spikes - coast or continue
            cmd.linear.x = self.max_speed * 0.3
            cmd.angular.z = 0.0
            
        self.current_command = cmd
        self.cmd_pub.publish(cmd)
        
    def direction_to_cmd(self, direction):
        """Convert 8-direction code to velocity command"""
        cmd = Twist()
        
        # Direction mapping (0-7)
        # 0: Forward, 1: Forward-Right, 2: Right, 3: Back-Right
        # 4: Back, 5: Back-Left, 6: Left, 7: Forward-Left
        
        speed = self.max_speed
        turn = 0.0
        
        if direction == 0:  # Forward
            speed = self.max_speed
            turn = 0.0
        elif direction == 1:  # Forward-Right
            speed = self.max_speed * 0.7
            turn = -self.turn_speed * 0.5
        elif direction == 2:  # Right
            speed = self.max_speed * 0.5
            turn = -self.turn_speed
        elif direction == 3:  # Back-Right
            speed = -self.max_speed * 0.3
            turn = -self.turn_speed * 0.7
        elif direction == 4:  # Back
            speed = -self.max_speed * 0.5
            turn = 0.0
        elif direction == 5:  # Back-Left
            speed = -self.max_speed * 0.3
            turn = self.turn_speed * 0.7
        elif direction == 6:  # Left
            speed = self.max_speed * 0.5
            turn = self.turn_speed
        elif direction == 7:  # Forward-Left
            speed = self.max_speed * 0.7
            turn = self.turn_speed * 0.5
            
        cmd.linear.x = speed
        cmd.angular.z = turn
        
        return cmd
        
    def get_statistics(self):
        """Get SNN performance statistics"""
        if self.total_updates == 0:
            return {}
            
        return {
            'avg_input_rate': self.spike_counts['input'] / self.total_updates,
            'avg_hidden_rate': self.spike_counts['hidden'] / self.total_updates,
            'avg_output_rate': self.spike_counts['output'] / self.total_updates,
            'total_updates': self.total_updates,
            'efficiency': self.spike_counts['output'] / max(1, self.spike_counts['input'] + self.spike_counts['hidden'])
        }


def main(args=None):
    rclpy.init(args=args)
    node = SNNController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        stats = node.get_statistics()
        node.get_logger().info(f'SNN Statistics: {stats}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
