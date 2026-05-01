#!/bin/bash
# Martian Swarm Quantum - Full Simulation Launch Script
# Run this to start the complete simulation system

set -e

echo "=============================================="
echo "  Martian Swarm Quantum - Simulation"
echo "=============================================="

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check dependencies
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "\033[0;31mError: $1 not found. Please install it first.\033[0m"
        echo "Run: ./scripts/setup_complete.sh"
        exit 1
    fi
}

# Function to run simulation
run_simulation() {
    echo "Starting Mars Swarm Simulation..."
    echo ""
    
    # Source ROS 2
    source /opt/ros/humble/setup.bash 2>/dev/null || true
    source "$PROJECT_ROOT/ros2_ws/install/setup.bash" 2>/dev/null || true
    
    # Set environment
    export ROS_DOMAIN_ID=42
    export GAZEBO_MODEL_PATH="$PROJECT_ROOT/gazebo_worlds/models:$GAZEBO_MODEL_PATH"
    export GAZEBO_RESOURCE_PATH="$PROJECT_ROOT/gazebo_worlds/worlds:$GAZEBO_RESOURCE_PATH"
    
    # Parse arguments
    NUM_ROVERS=5
    ENABLE_CHAOS=true
    ENABLE_QUANTUM=true
    USE_GAZEBO=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --rovers=*)
                NUM_ROVERS="${1#*=}"
                shift
                ;;
            --no-chaos)
                ENABLE_CHAOS=false
                shift
                ;;
            --no-quantum)
                ENABLE_QUANTUM=false
                shift
                ;;
            --no-gazebo)
                USE_GAZEBO=false
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --rovers=N     Number of rovers (default: 5)"
                echo "  --no-chaos     Disable chaos monkey"
                echo "  --no-quantum   Disable quantum map merge"
                echo "  --no-gazebo    Skip Gazebo simulation"
                echo "  --help         Show this help"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    echo "Configuration:"
    echo "  Rovers: $NUM_ROVERS"
    echo "  Chaos Monkey: $ENABLE_CHAOS"
    echo "  Quantum Map Merge: $ENABLE_QUANTUM"
    echo "  Gazebo Simulation: $USE_GAZEBO"
    echo ""
    
    # Start Gazebo (if available)
    if [ "$USE_GAZEBO" = true ] && command -v gz &> /dev/null; then
        echo "Starting Gazebo simulation..."
        gz sim "$PROJECT_ROOT/gazebo_worlds/worlds/martian_lava_tube.world" &
        GAZEBO_PID=$!
        sleep 3
    fi
    
    # Start ROS 2 launch
    echo "Starting ROS 2 swarm control..."
    cd "$PROJECT_ROOT/ros2_ws"
    
    ros2 launch swarm_control mars_swarm.launch.py \
        num_rovers:=$NUM_ROVERS \
        enable_chaos:=$ENABLE_CHAOS \
        enable_quantum:=$ENABLE_QUANTUM &
    
    MAIN_PID=$!
    
    # Cleanup function
    cleanup() {
        echo ""
        echo "Shutting down simulation..."
        kill $MAIN_PID 2>/dev/null || true
        kill $GAZEBO_PID 2>/dev/null || true
        echo "Simulation stopped."
    }
    
    trap cleanup SIGINT SIGTERM
    
    echo ""
    echo "Simulation running. Press Ctrl+C to stop."
    echo ""
    
    # Monitor
    while kill -0 $MAIN_PID 2>/dev/null; do
        sleep 1
    done
}

# Main
case "${BASH_SOURCE[0]}" in
    docker)
        echo "Starting Docker environment..."
        cd "$PROJECT_ROOT/docker"
        docker-compose up --build
        ;;
    *)
        run_simulation "$@"
        ;;
esac
