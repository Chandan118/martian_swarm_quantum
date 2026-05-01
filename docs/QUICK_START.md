# Quick Start Guide - Martian Swarm Quantum

## 5-Minute Setup

### 1. Clone and Setup (2 minutes)
```bash
cd ~/martian_swarm_quantum
chmod +x scripts/setup_complete.sh scripts/launch_simulation.sh
./scripts/setup_complete.sh
```

### 2. Launch Simulation (1 minute)
```bash
# Terminal 1: Start everything
source ~/.bashrc
ros2 launch swarm_control mars_swarm.launch.py

# Or with Docker
cd docker && docker-compose up
```

### 3. Monitor the Swarm (2 minutes)
```bash
# Check ROS 2 topics
ros2 topic list

# Watch swarm status
ros2 topic echo /swarm/status

# View chaos events
ros2 topic echo /chaos/event_log

# Monitor quantum progress
ros2 topic echo /quantum/status
```

## Common Commands

### Run Full Simulation
```bash
ros2 launch swarm_control mars_swarm.launch.py
```

### Run Individual Nodes
```bash
# Swarm control only
ros2 run swarm_control swarm_node

# Chaos monkey
ros2 run chaos_monkey chaos_node

# SNN controller
ros2 run snn_controller snn_node

# Quantum map merge
ros2 run quantum_map_merge quantum_node
```

### Custom Launch Options
```bash
# More rovers
ros2 launch swarm_control mars_swarm.launch.py num_rovers:=10

# Disable chaos testing
ros2 launch swarm_control mars_swarm.launch.py enable_chaos:=false

# Disable quantum (use simulated annealing)
ros2 launch swarm_control mars_swarm.launch.py enable_quantum:=false
```

## Using Research Rabbit

```bash
# Check project health
python3 scripts/research_rabbit.py diagnostics

# Analyze code for bugs
python3 scripts/research_rabbit.py analyze ros2_ws/src/swarm_control/

# Search for specific functionality
python3 scripts/research_rabbit.py search "obstacle avoidance"
```

## Troubleshooting

### "ROS 2 not found"
```bash
source /opt/ros/humble/setup.bash
```

### "Package not found"
```bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
```

### Build errors
```bash
cd ~/martian_swarm_quantum/ros2_ws
colcon build --symlink-install
```

## What's Next?

- Read the full [README.md](README.md) for complete documentation
- Check [M2_MAC_INSTALL.md](docs/M2_MAC_INSTALL.md) for Mac setup
- Run `./scripts/launch_simulation.sh --help` for launch options
