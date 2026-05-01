#!/bin/bash
# Phase 3: Blackout Stress Test - Running Script
# Time Required: ~40 hours

set -e

echo "=============================================="
echo "  Phase 3: Blackout Stress Test"
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

# Source ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || true
source "$PROJECT_ROOT/ros2_ws/install/setup.bash" 2>/dev/null || true

section "Phase 3 Goals"
cat << 'EOF'
This phase will test:
1. Chaos Monkey node functionality
2. Random mesh link severing
3. Complete blackout simulation
4. Rover survival mode activation

Expected deliverables:
✓ Chaos monkey functional
✓ Blackout detection working
✓ Survival mode validated
EOF

section "Step 1: Start Chaos Monkey"
echo "Starting Chaos Monkey..."
echo ""

cat << 'EOF'
=== TERMINAL 1: Chaos Monkey ===
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run chaos_monkey chaos_node
EOF

section "Step 2: Monitor Chaos Events"
echo "Monitor link status and chaos events:"
echo ""

cat << 'EOF'
=== TERMINAL 2: Monitor Link Status ===
source /opt/ros/humble/setup.bash
ros2 topic echo /chaos/link_status

=== TERMINAL 3: Monitor Survival Mode ===
source /opt/ros/humble/setup.bash
ros2 topic echo /chaos/survival_mode

=== TERMINAL 4: Monitor Events ===
source /opt/ros/humble/setup.bash
ros2 topic echo /chaos/event_log
EOF

section "Manual Control Commands"
echo "Control chaos monkey manually:"
echo ""

cat << 'EOF'
# Trigger a blackout manually
ros2 service call /chaos/trigger_blackout std_srvs/srv/Empty {}

# End current blackout
ros2 service call /chaos/end_blackout std_srvs/srv/Empty {}

# Get chaos status
ros2 service call /chaos/get_status std_srvs/srv/Empty {}

# Set parameters
ros2 param set /chaos_monkey blackout_probability 0.01
ros2 param set /chaos_monkey link_failure_prob 0.05
ros2 param set /chaos_monkey auto_trigger true
EOF

section "Chaos Parameters"
cat << 'EOF'
Configurable parameters:

blackout_probability: 0.001  (per second, chance of random blackout)
link_failure_prob: 0.01      (per second per link, chance of link failure)
max_blackout_duration: 180.0  (maximum blackout length in seconds)
min_blackout_duration: 30.0   (minimum blackout length in seconds)
auto_trigger: true           (enable automatic chaos events)

Blackout Types:
- instant: All links fail immediately
- gradual: Links fail progressively
- pulsing: Intermittent connectivity
EOF

section "Expected Output"
cat << 'EOF'
[WARN] [chaos_monkey]: Chaos Monkey initialized
[WARN] [chaos_monkey]: WARNING: Chaos testing is ACTIVE
[WARN] [chaos_monkey]: BLACKOUT STARTED - Type: instant
[WARN] [chaos_monkey]: Duration: 120 seconds
[WARN] [chaos_monkey]: Link failure: rover_0 <-> rover_1
[WARN] [chaos_monkey]: Link failure: rover_2 <-> rover_4
[WARN] [chaos_monkey]: rover_3 is now ISOLATED!
[INFO] [chaos_monkey]: BLACKOUT ENDED - Communications restored
[INFO] [chaos_monkey]: Total blackouts this session: 3
EOF

section "Testing Scenarios"
echo "Test different scenarios:"
echo ""

cat << 'EOF'
# Light chaos (5% link failures)
ros2 param set /chaos_monkey link_failure_prob 0.05
ros2 param set /chaos_monkey blackout_probability 0.0001

# Medium chaos (10% link failures)
ros2 param set /chaos_monkey link_failure_prob 0.1
ros2 param set /chaos_monkey blackout_probability 0.001

# Heavy chaos (20% link failures)
ros2 param set /chaos_monkey link_failure_prob 0.2
ros2 param set /chaos_monkey blackout_probability 0.01

# Disable auto-trigger (manual only)
ros2 param set /chaos_monkey auto_trigger false
EOF

section "Results Collection"
echo "Collect test results:"
echo ""

cat << 'EOF'
# Save chaos events to file
ros2 topic echo /chaos/event_log > ~/martian_swarm_quantum/results/chaos_events.log &

# Run experiment for a period
sleep 3600  # 1 hour

# Stop recording
pkill -f "ros2 topic echo /chaos/event_log"

# View results
cat ~/martian_swarm_quantum/results/chaos_events.log
EOF

section "Cleanup"
echo "To stop Phase 3:"
echo "  Ctrl+C in each terminal"
echo "  pkill -f chaos_node"

echo ""
echo -e "${GREEN}=============================================="
echo "  Phase 3 Ready!"
echo "  Follow the commands above to start"
echo "==============================================${NC}"
