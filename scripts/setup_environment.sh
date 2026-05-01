#!/bin/bash
# Martian Swarm Quantum - Complete Environment Setup
# Installs all dependencies for the project

set -e

echo "=============================================="
echo "  Martian Swarm Quantum"
echo "  Complete Environment Setup"
echo "=============================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "\033[0;31mError: Do not run as root. Run as your normal user.\033[0m"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

section() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}!${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Detect OS
section "System Check"
if grep -q "Ubuntu 22.04" /etc/os-release; then
    success "Ubuntu 22.04 LTS detected"
else
    warning "This setup is optimized for Ubuntu 22.04 LTS"
fi

# Project directory
PROJECT_DIR="$HOME/martian_swarm_quantum"
if [ ! -d "$PROJECT_DIR" ]; then
    error "Project directory not found at $PROJECT_DIR"
    echo "Please clone or copy the project first."
    exit 1
fi

success "Project directory: $PROJECT_DIR"

# ============================================
# 1. Install System Dependencies
# ============================================
section "Installing System Dependencies"

sudo apt update
sudo apt install -y \
    software-properties-common \
    gnupg \
    curl \
    git \
    tmux \
    htop \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    python3-yaml \
    python3-colcon-common-extensions \
    python3-rosdep \
    build-essential \
    cmake \
    libboost-all-dev \
    libeigen3-dev

success "System dependencies installed"

# ============================================
# 2. Install ROS 2 Humble
# ============================================
section "Installing ROS 2 Humble"

if [ -f "/opt/ros/humble/setup.bash" ]; then
    success "ROS 2 Humble already installed"
else
    echo "Installing ROS 2 Humble (this may take 20-30 minutes)..."
    
    sudo sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list'
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
    sudo apt update
    sudo apt install -y ros-humble-desktop ros-humble-ros-base
    
    success "ROS 2 Humble installed"
fi

# Source ROS 2
source /opt/ros/humble/setup.bash

# Initialize rosdep
if [ ! -f "$HOME/.rosdep/init.py" ]; then
    sudo rosdep init
fi
rosdep update

success "ROS 2 setup complete"

# ============================================
# 3. Install Gazebo Fortress
# ============================================
section "Installing Gazebo Fortress"

if command -v gz &> /dev/null; then
    GZ_VERSION=$(gz sim --version 2>&1 | head -1 || echo "unknown")
    success "Gazebo already installed: $GZ_VERSION"
else
    echo "Installing Gazebo Fortress (this may take 10-20 minutes)..."
    
    sudo wget https://packages.osrfoundation.org/gazebo.pub -O /tmp/packages.osrfoundation.org.gazebo.pub
    sudo apt-key add /tmp/packages.osrfoundation.org.gazebo.pub
    sudo sh -c "echo 'deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main' > /etc/apt/sources.list.d/gazebo-stable.list"
    sudo apt update
    sudo apt install -y gz-garden
    
    success "Gazebo Fortress installed"
fi

# ============================================
# 4. Install Python Packages
# ============================================
section "Installing Python Packages"

pip3 install --upgrade pip

pip3 install \
    numpy \
    scipy \
    matplotlib \
    pyyaml \
    transforms3d \
    opencv-python \
    Pillow \
    cirq \
    cirq-core

success "Python packages installed"

# Verify Cirq
if python3 -c "import cirq" 2>/dev/null; then
    success "Google Cirq installed"
else
    warning "Cirq installation may have failed - install manually: pip3 install cirq"
fi

# ============================================
# 5. Build ROS 2 Workspace
# ============================================
section "Building ROS 2 Workspace"

cd "$PROJECT_DIR/ros2_ws"

if [ -f "build" ]; then
    warning "Workspace already built - rebuilding..."
    rm -rf build install log
fi

colcon build --symlink-install

if [ $? -eq 0 ]; then
    success "ROS 2 workspace built"
else
    error "Workspace build failed"
    exit 1
fi

# ============================================
# 6. Install Docker
# ============================================
section "Installing Docker"

if command -v docker &> /dev/null; then
    success "Docker already installed"
else
    echo "Installing Docker..."
    sudo apt install -y docker.io docker-compose
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    warning "Docker installed. You may need to log out and back in for group changes to take effect."
fi

# ============================================
# 7. Setup Environment Variables
# ============================================
section "Setting Up Environment Variables"

# Add to .bashrc
BASHRC_LINE="[ -f $PROJECT_DIR/ros2_ws/install/setup.bash ] && source $PROJECT_DIR/ros2_ws/install/setup.bash"

if ! grep -q "$PROJECT_DIR/ros2_ws/install/setup.bash" "$HOME/.bashrc"; then
    echo "" >> "$HOME/.bashrc"
    echo "# Martian Swarm Quantum" >> "$HOME/.bashrc"
    echo "source $PROJECT_DIR/ros2_ws/install/setup.bash" >> "$HOME/.bashrc"
    echo "export ROS_DOMAIN_ID=42" >> "$HOME/.bashrc"
    echo "export GAZEBO_MODEL_PATH=$PROJECT_DIR/gazebo_worlds/models:\$GAZEBO_MODEL_PATH" >> "$HOME/.bashrc"
    success "Environment variables added to .bashrc"
else
    success "Environment variables already configured"
fi

# Create setup script for current session
source "$PROJECT_DIR/ros2_ws/install/setup.bash"
export ROS_DOMAIN_ID=42
export GAZEBO_MODEL_PATH="$PROJECT_DIR/gazebo_worlds/models:$GAZEBO_MODEL_PATH"

success "Environment configured for current session"

# ============================================
# 8. Make Scripts Executable
# ============================================
section "Making Scripts Executable"

chmod +x "$PROJECT_DIR/scripts/"*.sh
chmod +x "$PROJECT_DIR/scripts/"*.py 2>/dev/null || true

success "Scripts made executable"

# ============================================
# Completion
# ============================================
section "Setup Complete!"

echo ""
echo -e "${GREEN}=============================================="
echo "  Installation Complete!"
echo "==============================================${NC}"
echo ""
echo "To get started:"
echo ""
echo "1. Source the environment (or open a new terminal):"
echo "   source ~/.bashrc"
echo ""
echo "2. Launch the simulation:"
echo "   cd $PROJECT_DIR"
echo "   ./scripts/launch_simulation.sh"
echo ""
echo "3. Or run specific phases:"
echo "   ./scripts/run_phase1.sh  # Environment & Storm (~40 hours)"
echo "   ./scripts/run_phase2.sh  # SNN Swarm Setup (~80 hours)"
echo "   ./scripts/run_phase3.sh  # Blackout Stress Test (~40 hours)"
echo "   ./scripts/run_phase4.sh  # Quantum Map Recovery (~150 hours)"
echo "   ./scripts/run_phase5.sh  # GitHub & Polish (~40 hours)"
echo ""
echo "4. Documentation:"
echo "   cat $PROJECT_DIR/docs/SETUP_GUIDE.md"
echo "   cat $PROJECT_DIR/docs/PHASE_GUIDES.md"
echo ""
echo "5. Quick test (run experiments):"
echo "   python3 $PROJECT_DIR/run_experiments.py"
echo ""

# Verify installation
echo "Verification:"
echo ""
echo -n "  ROS 2: "
if command -v ros2 &> /dev/null; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL${NC}"; fi

echo -n "  Gazebo: "
if command -v gz &> /dev/null; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL${NC}"; fi

echo -n "  Python: "
if python3 -c "import numpy; import cirq" 2>/dev/null; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL${NC}"; fi

echo -n "  Workspace: "
if [ -f "$PROJECT_DIR/ros2_ws/install/setup.bash" ]; then echo -e "${GREEN}OK${NC}"; else echo -e "${RED}FAIL${NC}"; fi

echo ""
