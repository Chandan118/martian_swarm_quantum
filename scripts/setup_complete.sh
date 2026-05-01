#!/bin/bash
# Martian Swarm Quantum - Complete Setup Script
# Ubuntu 22.04+ Required
# Run: chmod +x setup_complete.sh && ./setup_complete.sh

set -e

echo "=============================================="
echo "  Martian Swarm Quantum - Complete Setup"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Ubuntu
if ! grep -q "Ubuntu 22.04\|Ubuntu 24.04" /etc/os-release; then
    echo -e "${RED}Error: This setup requires Ubuntu 22.04 LTS or 24.04 LTS${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}[1/7] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${BLUE}[2/7] Installing ROS 2 Humble...${NC}"
if [ ! -f "/opt/ros/humble/setup.bash" ]; then
    sudo apt install -y software-properties-common curl
    sudo add-apt-repository universe
    sudo add-apt-repository "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main"
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
    sudo apt update
    sudo apt install -y ros-humble-desktop ros-humble-ros-base
    sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-vcstool
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo -e "${GREEN}ROS 2 Humble installed${NC}"
else
    echo -e "${YELLOW}ROS 2 Humble already installed${NC}"
fi

echo -e "${BLUE}[3/7] Installing Gazebo Fortress...${NC}"
if ! command -v gz &> /dev/null; then
    sudo wget https://packages.osrfoundation.org/gazebo.pub -O /tmp/packages.osrfoundation.org.gazebo.pub
    sudo apt-key add /tmp/packages.osrfoundation.org.gazebo.pub
    sudo sh -c "echo 'deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main' > /etc/apt/sources.list.d/gazebo-stable.list"
    sudo apt update
    sudo apt install -y gz-garden
    echo -e "${GREEN}Gazebo Fortress installed${NC}"
else
    echo -e "${YELLOW}Gazebo already installed${NC}"
fi

echo -e "${BLUE}[4/7] Installing Python dependencies...${NC}"
pip3 install --break-system-packages numpy scipy transforms3d pyyaml matplotlib Pillow opencv-python

echo -e "${BLUE}[5/7] Installing system utilities...${NC}"
sudo apt install -y git tmux htop tree

echo -e "${BLUE}[6/7] Building ROS 2 workspace...${NC}"
cd "$PROJECT_ROOT/ros2_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install
echo "source $PROJECT_ROOT/ros2_ws/install/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc

echo -e "${BLUE}[7/7] Final configuration...${NC}"
export GAZEBO_MODEL_PATH="$PROJECT_ROOT/gazebo_worlds/models:$GAZEBO_MODEL_PATH"
export GAZEBO_RESOURCE_PATH="$PROJECT_ROOT/gazebo_worlds/worlds:$GAZEBO_RESOURCE_PATH"
echo "export GAZEBO_MODEL_PATH=$PROJECT_ROOT/gazebo_worlds/models:\$GAZEBO_MODEL_PATH" >> ~/.bashrc
echo "export GAZEBO_RESOURCE_PATH=$PROJECT_ROOT/gazebo_worlds/worlds:\$GAZEBO_RESOURCE_PATH" >> ~/.bashrc

echo ""
echo -e "${GREEN}=============================================="
echo "  Setup Complete!"
echo "==============================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Source: source ~/.bashrc"
echo "  2. Launch simulation: ros2 launch swarm_control mars_swarm.launch.py"
echo "  3. Or use Docker: cd $PROJECT_ROOT/docker && docker-compose up"
echo ""
echo "Project location: $PROJECT_ROOT"
