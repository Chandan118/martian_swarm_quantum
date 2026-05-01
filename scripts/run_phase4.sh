#!/bin/bash
# Phase 4: Quantum Map Recovery - Running Script
# Time Required: ~150 hours

set -e

echo "=============================================="
echo "  Phase 4: Quantum Map Recovery"
echo "  Estimated Time: ~150 hours"
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

# Check for Cirq
echo "Checking Python packages..."
if python3 -c "import cirq" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Google Cirq installed"
else
    echo -e "${YELLOW}!${NC} Google Cirq not installed"
    echo "  Install with: pip3 install cirq cirq-core"
fi

# Source ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || true
source "$PROJECT_ROOT/ros2_ws/install/setup.bash" 2>/dev/null || true

section "Phase 4 Goals"
cat << 'EOF'
This phase will implement:
1. Map fragment collection from rovers
2. QUBO formulation for NP-hard problem
3. Google Cirq quantum integration
4. Simulated annealing fallback

Expected deliverables:
✓ QUBO formulation working
✓ Cirq integration functional
✓ Map merging successful
✓ Fallback solver working
EOF

section "Step 1: Install Google Cirq"
echo "Installing Google Cirq..."
echo ""

cat << 'EOF'
# Install Cirq
pip3 install cirq cirq-core

# Verify installation
python3 -c "import cirq; print('Cirq version:', cirq.__version__)"
EOF

if ! python3 -c "import cirq" 2>/dev/null; then
    echo ""
    echo "Installing Cirq now..."
    pip3 install cirq cirq-core
fi

section "Step 2: Start Quantum Node"
echo "Starting Quantum Map Merge node..."
echo ""

cat << 'EOF'
=== TERMINAL 1: Quantum Node ===
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run quantum_map_merge quantum_node
EOF

section "Step 3: Collect Map Fragments"
echo "Collect map fragments from rovers:"
echo ""

cat << 'EOF'
=== TERMINAL 2: Publish Sample Map Fragment ===
source /opt/ros/humble/setup.bash

# Publish fragment from rover_0
ros2 topic pub /swarm/map_fragment std_msgs/String \
"{data: '{\"rover_id\": 0, \"timestamp\": 1234567890, \"grid\": [[0,0,100],[0,100,0]]}'}" -1

# Publish fragment from rover_1
ros2 topic pub /swarm/map_fragment std_msgs/String \
"{data: '{\"rover_id\": 1, \"timestamp\": 1234567891, \"grid\": [[100,0],[0,0]]}'}" -1

# Publish fragment from rover_2
ros2 topic pub /swarm/map_fragment std_msgs/String \
"{data: '{\"rover_id\": 2, \"timestamp\": 1234567892, \"grid\": [[0,100],[100,0]]}'}" -1
EOF

section "Step 4: Trigger Map Merge"
echo "Trigger the quantum map merge:"
echo ""

cat << 'EOF'
=== TERMINAL 3: Trigger Merge ===
source /opt/ros/humble/setup.bash

# Trigger merge manually
ros2 service call /quantum/trigger_merge std_srvs/srv/Empty {}

# Or wait for blackout end (automatic)
# When blackout ends, quantum node collects fragments for 60s, then merges
EOF

section "Step 5: Monitor Results"
echo "Monitor quantum optimization results:"
echo ""

cat << 'EOF'
=== TERMINAL 4: Monitor Merged Map ===
source /opt/ros/humble/setup.bash
ros2 topic echo /quantum/merged_map

=== TERMINAL 5: Monitor Optimization ===
source /opt/ros/humble/setup.bash
ros2 topic echo /quantum/result

=== TERMINAL 6: Monitor Progress ===
source /opt/ros/humble/setup.bash
ros2 topic echo /quantum/progress
EOF

section "Expected Output"
cat << 'EOF'
[INFO] [quantum_map_merge]: EXECUTING QUANTUM MAP MERGE
[INFO] [quantum_map_merge]: Step 1: Creating QUBO formulation
[INFO] [quantum_map_merge]: QUBO size: 20x20
[INFO] [quantum_map_merge]: Step 2: Running quantum optimization
[INFO] [quantum_map_merge]: Optimization complete - Cost: -2.77
[INFO] [quantum_map_merge]: Step 3: Parsing optimal alignment
[INFO] [quantum_map_merge]: Step 4: Stitching maps
[INFO] [quantum_map_merge]: Step 5: Publishing merged map
[INFO] [quantum_map_merge]: QUANTUM MAP MERGE COMPLETE
EOF

section "Quantum Parameters"
cat << 'EOF'
Configurable parameters:

use_quantum: true           (use quantum optimization vs. simulated annealing)
fragment_timeout: 60.0      (seconds to collect fragments after blackout)
overlap_threshold: 0.3      (minimum overlap for matching)
grid_resolution: 0.1         (meters per cell)

Set parameters:
ros2 param set /quantum_map_merge use_quantum false
ros2 param set /quantum_map_merge fragment_timeout 30.0
EOF

section "Testing Different Methods"
echo "Test with simulated annealing (faster):"
echo ""

cat << 'EOF'
# Use simulated annealing instead of quantum
ros2 param set /quantum_map_merge use_quantum false

# Re-run merge
ros2 service call /quantum/trigger_merge std_srvs/srv/Empty {}
EOF

echo ""
echo "Test with quantum optimization (slower but more accurate):"
echo ""

cat << 'EOF'
# Use real quantum
ros2 param set /quantum_map_merge use_quantum true

# Re-run merge
ros2 service call /quantum/trigger_merge std_srvs/srv/Empty {}
EOF

section "Results Analysis"
echo "Analyze merge results:"
echo ""

cat << 'EOF'
# View optimization result
ros2 topic echo /quantum/result

# The result contains:
# - success: boolean
# - cost: optimization cost value
# - num_fragments: how many fragments merged
# - alignments: rotation/position for each fragment
# - timestamp: when merge completed
EOF

section "Cleanup"
echo "To stop Phase 4:"
echo "  Ctrl+C in each terminal"
echo "  pkill -f quantum_node"

echo ""
echo -e "${GREEN}=============================================="
echo "  Phase 4 Ready!"
echo "  Follow the commands above to start"
echo "==============================================${NC}"
