#!/bin/bash
# Phase 1: Environment & Storm - Running Script
# Time Required: ~40 hours

set -e

echo "=============================================="
echo "  Phase 1: Environment & Storm"
echo "  Estimated Time: ~40 hours"
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
check_command "matlab"

# Source ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || true
source "$PROJECT_ROOT/ros2_ws/install/setup.bash" 2>/dev/null || true

section "Phase 1 Goals"
cat << 'EOF'
This phase will set up:
1. Gazebo Mars environment (lava tube/canyon)
2. MATLAB dust storm controller
3. ROS 2 integration for storm control
4. Sensor blinding effects

Expected deliverables:
✓ Gazebo world with Mars terrain
✓ Working dust storm simulation  
✓ ROS 2 integration working
EOF

section "Step 1: Verify Gazebo World"
if [ -f "$PROJECT_ROOT/gazebo_worlds/worlds/martian_lava_tube.world" ]; then
    echo -e "${GREEN}✓${NC} Martian lava tube world found"
else
    echo -e "${YELLOW}!${NC} World file not found - will use default Gazebo world"
fi

section "Step 2: Launch Gazebo with Mars Environment"
echo "Starting Gazebo simulation..."
echo "This will open the Gazebo GUI"
echo ""
echo "In another terminal, you can run:"
echo "  export GAZEBO_MODEL_PATH=$PROJECT_ROOT/gazebo_worlds/models:\$GAZEBO_MODEL_PATH"

if [ -f "$PROJECT_ROOT/gazebo_worlds/worlds/martian_lava_tube.world" ]; then
    gz sim "$PROJECT_ROOT/gazebo_worlds/worlds/martian_lava_tube.world" &
else
    echo "Launching default Gazebo world..."
    gz sim --headless-rendering &
fi

GAZEBO_PID=$!
echo "Gazebo started (PID: $GAZEBO_PID)"

section "Step 3: MATLAB Dust Storm Controller"
echo ""
echo "To run the MATLAB dust storm controller:"
echo ""
echo "1. Open MATLAB:"
echo "   matlab &"
echo ""
echo "2. In MATLAB command window, run:"
echo "   cd ~/martian_swarm_quantum/matlab_scripts"
echo "   DustStormController"
echo ""
echo "3. The GUI will open with storm controls"

section "Step 4: Verify ROS 2 Integration"
echo "Checking ROS 2 topics..."
echo ""

if ros2 topic list &>/dev/null; then
    echo "Available storm-related topics:"
    ros2 topic list | grep -E "(mars|dust|storm)" || echo "No storm topics yet - start MATLAB controller"
else
    echo -e "${RED}✗${NC} ROS 2 not running"
fi

section "Phase 1 Commands Summary"
cat << 'EOF'
=== TERMINAL 1: Gazebo ===
cd ~/martian_swarm_quantum
export GAZEBO_MODEL_PATH=$PWD/gazebo_worlds/models:$GAZEBO_MODEL_PATH
gz sim gazebo_worlds/worlds/martian_lava_tube.world

=== TERMINAL 2: MATLAB ===
matlab &
# Then in MATLAB:
cd ~/martian_swarm_quantum/matlab_scripts
DustStormController

=== TERMINAL 3: Monitor Topics ===
source /opt/ros/humble/setup.bash
ros2 topic list
ros2 topic echo /mars_environment/dust_intensity
EOF

section "Cleanup"
echo "To stop Phase 1:"
echo "  kill $GAZEBO_PID"
echo "  Close MATLAB window"

echo ""
echo -e "${GREEN}=============================================="
echo "  Phase 1 Ready!"
echo "  Follow the commands above to start"
echo "==============================================${NC}"

# Keep script running for reference
echo ""
echo "Press Ctrl+C to exit this script (Gazebo will keep running)"
wait $GAZEBO_PID
