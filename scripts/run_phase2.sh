#!/bin/bash
# Phase 2: SNN Swarm Setup - Running Script
# Time Required: ~80 hours

set -e

echo "=============================================="
echo "  Phase 2: SNN Swarm Setup"
echo "  Estimated Time: ~80 hours"
echo "=============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

# Check prerequisites
section "Checking Prerequisites"

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 installed"
    else
        echo -e "${RED}✗${NC} $1 NOT installed - run setup_environment.sh first"
        exit 1
    fi
}

check_command "ros2"
check_command "gz"

# Source ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || true
source "$PROJECT_ROOT/ros2_ws/install/setup.bash" 2>/dev/null || true

section "Phase 2 Goals"
cat << 'EOF'
This phase will set up:
1. 5-10 configurable rovers in Gazebo
2. SNN-based obstacle avoidance
3. Swarm coordination protocol
4. Ant-pheromone inspired navigation

Expected deliverables:
✓ Rovers spawn successfully
✓ SNN obstacle detection working
✓ Swarm navigation functional
EOF

section "Step 1: Build ROS 2 Workspace"
echo "Building workspace..."
cd "$PROJECT_ROOT/ros2_ws"
colcon build --symlink-install

section "Step 2: Launch Swarm System"
echo ""
echo "Starting swarm with 5 rovers..."
echo "Options:"
echo "  --rovers=N    Number of rovers (default: 5)"
echo "  --no-gazebo   Skip Gazebo (use existing)"
echo ""

NUM_ROVERS=5
if [ "$1" == "--rovers="* ]]; then
    NUM_ROVERS="${1#*=}"
fi

echo "Launching with $NUM_ROVERS rovers..."

section "Step 3: Component Startup"
cat << 'EOF'
=== TERMINAL 1: Gazebo (if not running) ===
cd ~/martian_swarm_quantum
export GAZEBO_MODEL_PATH=$PWD/gazebo_worlds/models:$GAZEBO_MODEL_PATH
gz sim gazebo_worlds/worlds/martian_lava_tube.world

=== TERMINAL 2: Swarm Control ===
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run swarm_control swarm_node

=== TERMINAL 3: SNN Controller ===
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run snn_controller snn_node

=== TERMINAL 4: Monitor ===
source /opt/ros/humble/setup.bash
ros2 topic echo /swarm/status
ros2 topic echo /snn/avoidance_direction
EOF

section "Phase 2 Using Launch File"
echo "Or use the launch file:"
echo ""
echo "  source ~/martian_swarm_quantum/ros2_ws/install/setup.bash"
echo "  ros2 launch swarm_control mars_swarm.launch.py num_rovers:=$NUM_ROVERS"
echo ""

section "Verification Commands"
cat << 'EOF'
After starting, verify with:

# Check rovers
ros2 topic list | grep rover

# Check swarm status
ros2 topic echo /swarm/status

# Check SNN output
ros2 topic echo /snn/avoidance_direction

# Check mesh topology
ros2 topic echo /swarm/topology
EOF

section "Expected Output"
cat << 'EOF'
[INFO] [swarm_control]: Swarm Control initialized with 5 rovers
[INFO] [swarm_control]: Spawned rover_0 at (-10.0, -30.0)
[INFO] [swarm_control]: Spawned rover_1 at (-5.0, -30.0)
[INFO] [swarm_control]: Spawned rover_2 at (0.0, -30.0)
[INFO] [swarm_control]: Spawned rover_3 at (5.0, -30.0)
[INFO] [swarm_control]: Spawned rover_4 at (10.0, -30.0)
[INFO] [snn_controller]: SNN Controller initialized
[INFO] [snn_controller]: Architecture: 8 -> 16 -> 8
EOF

section "Cleanup"
echo "To stop Phase 2:"
echo "  Ctrl+C in each terminal"
echo "  pkill -f swarm_node"
echo "  pkill -f snn_node"

echo ""
echo -e "${GREEN}=============================================="
echo "  Phase 2 Ready!"
echo "  Follow the commands above to start"
echo "==============================================${NC}"
