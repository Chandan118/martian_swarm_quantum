#!/bin/bash
# Martian Swarm Quantum - Complete Installation Script
# Installs ROS 2, Gazebo, and all dependencies

set -e

echo "=============================================="
echo "  Martian Swarm Quantum - Installation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check OS
echo -e "${YELLOW}Checking system requirements...${NC}"
if ! grep -q "Ubuntu 22.04" /etc/os-release; then
    echo -e "${RED}Error: This setup requires Ubuntu 22.04 LTS${NC}"
    exit 1
fi

# Install ROS 2 Humble
echo -e "${YELLOW}Installing ROS 2 Humble...${NC}"
if ! command -v /opt/ros/humble/setup.bash &> /dev/null; then
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository universe
    sudo add-apt-repository "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main"
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
    sudo apt update
    sudo apt install -y ros-humble-desktop ros-humble-ros-base
    sudo apt install -y python3-colcon-common-extensions python3-rosdep
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
else
    echo -e "${GREEN}ROS 2 Humble already installed${NC}"
fi

# Source ROS
source /opt/ros/humble/setup.bash

# Install Gazebo Fortress
echo -e "${YELLOW}Installing Gazebo Fortress...${NC}"
if ! command -v gz &> /dev/null; then
    sudo wget https://packages.osrfoundation.org/gazebo.pub -O /tmp/packages.osrfoundation.org.gazebo.pub
    sudo apt-key add /tmp/packages.osrfoundation.org.gazebo.pub
    sudo sh -c "echo 'deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main' > /etc/apt/sources.list.d/gazebo-stable.list"
    sudo apt update
    sudo apt install -y gz-garden
else
    echo -e "${GREEN}Gazebo already installed${NC}"
fi

# Install additional dependencies
echo -e "${YELLOW}Installing additional dependencies...${NC}"
sudo apt install -y \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-yaml \
    python3-transforms3d \
    git \
    tmux \
    htop

# Python packages
echo -e "${YELLOW}Installing Python packages...${NC}"
pip3 install --user numpy scipy transforms3d pyyaml opencv-python Pillow

# Build ROS 2 workspace
echo -e "${YELLOW}Building ROS 2 workspace...${NC}"
cd "$(dirname "$0")/ros2_ws"

# Initialize colcon
if [ ! -f "build" ]; then
    colcon build --symlink-install
fi

# Source workspace
echo "source $(pwd)/install/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc

# Docker installation
echo -e "${YELLOW}Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    sudo apt install -y docker.io docker-compose
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. You may need to log out and back in.${NC}"
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

echo ""
echo -e "${GREEN}=============================================="
echo "  Installation Complete!"
echo "==============================================${NC}"
echo ""
echo "To get started:"
echo "  1. Source the workspace: source ~/martian_swarm_quantum/ros2_ws/install/setup.bash"
echo "  2. Launch the simulation: ros2 launch swarm_control mars_swarm.launch.py"
echo "  3. Or use Docker: cd docker && docker-compose up"
echo ""
