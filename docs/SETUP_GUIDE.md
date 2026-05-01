# Martian Swarm Quantum - Complete Setup Guide

**Total Project Time: ~300-350 hours (2-3 months full-time)**

This is a groundbreaking research platform combining:
- ROS 2 Humble (rover swarm coordination)
- Neuromorphic Computing (SNN-based navigation)
- Quantum Computing (map merging with Google Cirq)
- Gazebo Fortress (Mars environment simulation)

---

## Project Structure

```
martian_swarm_quantum/
├── docs/                           # Documentation
│   ├── SETUP_GUIDE.md             # This file
│   ├── PHASE_GUIDES.md            # Phase-by-phase running instructions
│   └── TROUBLESHOOTING.md         # Common issues and fixes
├── docker/                         # Docker configurations
│   ├── Dockerfile.ros2           # ROS 2 container
│   ├── Dockerfile.gazebo         # Gazebo container
│   ├── Dockerfile.quantum         # Quantum computing container
│   └── docker-compose.yml         # Full stack orchestration
├── gazebo_worlds/                 # Gazebo simulation
│   └── worlds/
│       └── martian_lava_tube.world # Martian lava tube environment
├── matlab_scripts/                 # MATLAB dust storm controller
│   └── dust_storm_controller.m    # Dynamic dust storm simulation
├── ros2_ws/                       # ROS 2 workspace
│   └── src/
│       ├── chaos_monkey/          # Communication stress testing
│       ├── quantum_map_merge/     # Quantum map merging
│       ├── snn_controller/        # Spiking neural network control
│       └── swarm_control/         # Rover swarm coordination
├── scripts/                       # Utility scripts
│   ├── setup_environment.sh      # Full environment setup
│   ├── run_phase1.sh            # Phase 1: Environment & Storm
│   ├── run_phase2.sh             # Phase 2: SNN Swarm Setup
│   ├── run_phase3.sh             # Phase 3: Blackout Stress Test
│   ├── run_phase4.sh             # Phase 4: Quantum Map Recovery
│   ├── run_phase5.sh             # Phase 5: GitHub & Polish
│   ├── launch_simulation.sh      # Full simulation launcher
│   ├── research_rabbit.py         # AI research assistant
│   └── bug_fixer.py              # Automated bug fixer
├── results/                       # Experiment results (generated)
├── QUICKSTART.md                 # 5-minute overview
└── README.md                     # Project overview
```

---

## Prerequisites

### Hardware Requirements
- **CPU**: 8+ cores (recommended: 16 cores)
- **RAM**: 16GB minimum (recommended: 32GB)
- **GPU**: CUDA-compatible GPU (for quantum simulation)
- **Storage**: 50GB free space
- **OS**: Ubuntu 22.04 LTS

### Software Requirements
- Ubuntu 22.04 LTS
- ROS 2 Humble
- Gazebo Fortress (Garden)
- MATLAB (for dust storm controller)
- Python 3.10+
- Docker & Docker Compose
- Google Cirq (for quantum computing)

---

## Quick Setup (30 minutes)

### Step 1: Clone/Update the Project

```bash
cd ~/martian_swarm_quantum
git pull origin main  # If already cloned
```

### Step 2: Run Full Environment Setup

```bash
cd ~/martian_swarm_quantum
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

This script will:
- Install ROS 2 Humble
- Install Gazebo Fortress
- Install Python dependencies
- Build ROS 2 workspace
- Setup Docker containers
- Install Google Cirq

### Step 3: Verify Installation

```bash
# Source ROS 2
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash

# Check ROS 2
ros2 doctor

# Check Gazebo
gz sim --version

# Check Python packages
python3 -c "import cirq; print('Cirq installed')"
python3 -c "import numpy; print('NumPy installed')"
```

---

## Phase-by-Phase Setup

### Phase 1: Environment & Storm (~40 hours)

**Goal**: Build Gazebo Mars world and MATLAB dust storm controller

**Setup**:
```bash
# Verify Gazebo world exists
ls -la ~/martian_swarm_quantum/gazebo_worlds/worlds/

# Verify MATLAB script exists
ls -la ~/martian_swarm_quantum/matlab_scripts/

# Run Phase 1
./scripts/run_phase1.sh
```

**What it does**:
- Launches Gazebo with Martian lava tube world
- Starts MATLAB dust storm controller
- Connects storm to ROS 2 network

**Deliverables**:
- [ ] Gazebo world with Mars terrain
- [ ] Working dust storm simulation
- [ ] ROS 2 integration working

---

### Phase 2: SNN Swarm Setup (~80 hours)

**Goal**: Connect neuromorphic algorithms to ROS 2 rovers

**Setup**:
```bash
# Verify SNN controller exists
ls -la ~/martian_swarm_quantum/ros2_ws/src/snn_controller/

# Verify swarm control exists
ls -la ~/martian_swarm_quantum/ros2_ws/src/swarm_control/

# Run Phase 2
./scripts/run_phase2.sh
```

**What it does**:
- Spawns 5-10 rovers in Gazebo
- Connects SNN controllers to each rover
- Tests obstacle avoidance
- Validates swarm coordination

**Deliverables**:
- [ ] Rovers spawn successfully
- [ ] SNN obstacle detection working
- [ ] Swarm navigation functional

---

### Phase 3: Blackout Stress Test (~40 hours)

**Goal**: Test rover resilience under communication failures

**Setup**:
```bash
# Verify chaos monkey exists
ls -la ~/martian_swarm_quantum/ros2_ws/src/chaos_monkey/

# Run Phase 3
./scripts/run_phase3.sh
```

**What it does**:
- Triggers random link failures
- Simulates complete blackouts
- Tests survival mode
- Records rover behavior

**Deliverables**:
- [ ] Chaos monkey functional
- [ ] Blackout detection working
- [ ] Survival mode validated

---

### Phase 4: Quantum Map Recovery (~150 hours)

**Goal**: Implement quantum map merging algorithm

**Setup**:
```bash
# Verify quantum node exists
ls -la ~/martian_swarm_quantum/ros2_ws/src/quantum_map_merge/

# Install Google Cirq
pip3 install cirq

# Run Phase 4
./scripts/run_phase4.sh
```

**What it does**:
- Collects map fragments from rovers
- Creates QUBO matrix
- Runs quantum optimization (Cirq)
- Merges maps with fallback to simulated annealing

**Deliverables**:
- [ ] QUBO formulation working
- [ ] Cirq integration functional
- [ ] Map merging successful
- [ ] Fallback solver working

---

### Phase 5: GitHub & Polish (~40 hours)

**Goal**: Package for open-source release

**Setup**:
```bash
# Build Docker containers
cd ~/martian_swarm_quantum/docker
docker-compose build

# Run full stack test
docker-compose up

# Run Phase 5
./scripts/run_phase5.sh
```

**What it does**:
- Builds all Docker containers
- Creates documentation
- Runs integration tests
- Prepares GitHub release

**Deliverables**:
- [ ] Docker containers working
- [ ] Full documentation
- [ ] GitHub repository ready

---

## Running the Full Simulation

### Method 1: Full Stack (Recommended)

```bash
cd ~/martian_swarm_quantum

# Source ROS 2
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash

# Launch everything
./scripts/launch_simulation.sh --rovers=5
```

### Method 2: Docker (For Mac/Windows)

```bash
cd ~/martian_swarm_quantum/docker
docker-compose up
```

### Method 3: Individual Components

```bash
# Terminal 1: Gazebo
gz sim gazebo_worlds/worlds/martian_lava_tube.world

# Terminal 2: Swarm Control
ros2 run swarm_control swarm_node

# Terminal 3: Chaos Monkey
ros2 run chaos_monkey chaos_node

# Terminal 4: SNN Controller
ros2 run snn_controller snn_node

# Terminal 5: Quantum Map Merge
ros2 run quantum_map_merge quantum_node
```

---

## Configuration

### Rover Parameters

Edit `ros2_ws/src/swarm_control/config/default.yaml`:

```yaml
num_rovers: 5
spawn_area_x: 20.0
spawn_area_y: 60.0
comm_range: 15.0
mesh_topology: dynamic
```

### Dust Storm Parameters

Edit `matlab_scripts/dust_storm_controller.m`:

```matlab
minStormDuration = 30;   % seconds
maxStormDuration = 300;  % 5 minutes
minInterval = 45;        % seconds between storms
maxInterval = 180;       % 3 minutes between storms
visionImpactFactor = 0.8;
lidarImpactFactor = 0.3;
```

### Chaos Parameters

Edit `ros2_ws/src/chaos_monkey/config/default.yaml`:

```yaml
blackout_probability: 0.001  # per second
link_failure_prob: 0.01      # per second per link
max_blackout_duration: 180.0 # seconds
min_blackout_duration: 30.0  # seconds
```

---

## Troubleshooting

### ROS 2 Issues

**Domain ID conflicts**:
```bash
export ROS_DOMAIN_ID=42
```

**Missing dependencies**:
```bash
rosdep install --from-paths ros2_ws/src --ignore-src -y
```

### Gazebo Issues

**Missing models**:
```bash
export GAZEBO_MODEL_PATH=~/martian_swarm_quantum/gazebo_worlds/models:$GAZEBO_MODEL_PATH
```

**Rendering problems**:
```bash
export GAZEBO_RENDERER=ogre2
```

### Docker Issues

**Permission denied**:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Memory issues**: Edit `docker/docker-compose.yml`:
```yaml
services:
  ros2:
    shm_size: '2gb'
```

---

## Next Steps

1. **Read the Phase Guides** (`docs/PHASE_GUIDES.md`)
2. **Install prerequisites** using `scripts/setup_environment.sh`
3. **Start with Phase 1** when ready
4. **Track progress** in the results folder

---

**Questions?** Check `docs/TROUBLESHOOTING.md` or run:
```bash
python3 scripts/research_rabbit.py diagnostics
```
