# M2 Mac ROS 2 Installation Guide

## Prerequisites

- Apple Silicon (M1/M2/M3) Mac
- macOS 12.6+ (Monterey or later)
- 16GB+ RAM recommended
- 50GB+ free disk space

## Option 1: Native Installation (Recommended for M2 Mac)

### Step 1: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Dependencies
```bash
brew install python@3.11 cmake git curl wget
brew install --cask xquartz
```

### Step 3: Install ROS 2 (via Docker - Native ROS 2 doesn't fully support M2)
Since ROS 2 Humble doesn't officially support macOS, use our Docker setup:

```bash
brew install --cask docker
```

### Step 4: Clone the Project
```bash
git clone https://github.com/yourusername/martian_swarm_quantum.git
cd martian_swarm_quantum
```

### Step 5: Run with Docker
```bash
cd docker
docker-compose up
```

## Option 2: Cross-Compilation with ROS 2 Docker on Mac

### Step 1: Install Docker Desktop for Mac
Download from: https://www.docker.com/products/docker-desktop/

### Step 2: Enable Rosetta (for x86_64 compatibility)
```bash
softwareupdate --install-rosetta
```

### Step 3: Run the Complete Docker Environment
```bash
cd ~/martian_swarm_quantum/docker
docker-compose -f docker-compose.yml up
```

## Option 3: Using colcon (Limited M2 Support)

### Step 1: Install Python and Dependencies
```bash
brew install python@3.11 pyenv
pyenv install 3.11.0
pyenv global 3.11.0
eval "$(pyenv init --path)"

pip3 install numpy scipy transforms3d pyyaml matplotlib Pillow
```

### Step 2: Try ROS 2 Source Installation (Experimental)
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
vcs import src < /path/to/ros2.repos

# This may have limited functionality on M2
colcon build --symlink-install
```

## M2 Mac Performance Notes

### GPU Acceleration
M2 chips have excellent Metal support. For Gazebo:
```bash
# Enable Metal rendering
export GAZEBO_RENDERER=ogre2
```

### Memory Management
M2 Macs handle ROS 2 simulations well with 16GB+ RAM:
- 5 rovers: ~8GB RAM
- 10 rovers: ~12GB RAM

### Disk Space
- ROS 2 Humble: ~5GB
- Gazebo Fortress: ~2GB
- Workspace: ~500MB

## Quick Start for M2 Mac

```bash
# 1. Install Docker Desktop
brew install --cask docker

# 2. Clone project
git clone https://github.com/yourusername/martian_swarm_quantum.git
cd martian_swarm_quantum

# 3. Start simulation
cd docker
docker-compose up
```

## Troubleshooting M2 Mac

### Rosetta 2 Issues
```bash
# Check if running ARM native
uname -m  # Should show arm64
```

### Docker Memory
Increase Docker memory in Docker Desktop > Settings > Resources:
- Minimum: 8GB
- Recommended: 16GB

### Port Conflicts
ROS 2 uses ports 7400-7409 for DDS. Ensure they're available:
```bash
lsof -i :7400-7409
```

## SSH to Linux from Mac for Full Experience

For the best experience, run ROS 2/Gazebo on a Linux machine and connect from Mac:

```bash
# On Mac
ssh -Y user@linux-machine

# In SSH session
source /opt/ros/humble/setup.bash
ros2 launch swarm_control mars_swarm.launch.py
```

## Research Rabbit Integration

On your M2 Mac, run Research Rabbit for AI assistance:

```bash
cd martian_swarm_quantum
python3 scripts/research_rabbit.py diagnostics
```
