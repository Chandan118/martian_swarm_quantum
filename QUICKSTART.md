# Martian Swarm Quantum - Quick Start Guide

**5-Minute Overview**

This is a groundbreaking research platform combining:
- ROS 2 Humble (rover swarm coordination)
- Neuromorphic Computing (SNN-based navigation)  
- Quantum Computing (map merging with Google Cirq)
- Gazebo Fortress (Mars environment simulation)

---

## TL;DR - Run Everything Now

```bash
cd ~/martian_swarm_quantum

# 1. Source environment
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash

# 2. Run experiments (no hardware needed)
python3 run_experiments.py

# 3. View results
ls results/
```

---

## Phase Breakdown (300-350 hours total)

| Phase | Description | Time |
|-------|-------------|------|
| Phase 1 | Environment & Storm | ~40 hours |
| Phase 2 | SNN Swarm Setup | ~80 hours |
| Phase 3 | Blackout Stress Test | ~40 hours |
| Phase 4 | Quantum Map Recovery | ~150 hours |
| Phase 5 | GitHub & Polish | ~40 hours |

---

## What Each Phase Does

### Phase 1: Environment & Storm (~40 hours)
Builds the Mars environment in Gazebo and MATLAB dust storm controller.

**Run:**
```bash
./scripts/run_phase1.sh
```

**You'll see:**
- Martian lava tube environment in Gazebo
- Dynamic dust storm simulation
- Vision and LiDAR sensor blinding effects

---

### Phase 2: SNN Swarm Setup (~80 hours)
Connects neuromorphic navigation to ROS 2 rovers.

**Run:**
```bash
./scripts/run_phase2.sh
```

**You'll see:**
- 5-10 rovers spawning in Gazebo
- SNN obstacle avoidance working
- Swarm coordination forming mesh network

---

### Phase 3: Blackout Stress Test (~40 hours)
Tests rover resilience under communication failures.

**Run:**
```bash
./scripts/run_phase3.sh
```

**You'll see:**
- Random mesh link severing
- Complete blackout simulation
- Rover survival mode activation

---

### Phase 4: Quantum Map Recovery (~150 hours)
Implements quantum-optimized map merging.

**Run:**
```bash
./scripts/run_phase4.sh
```

**You'll see:**
- Map fragments collected from rovers
- QUBO matrix created
- Google Cirq quantum optimization running
- Maps merged with 85%+ coverage

---

### Phase 5: GitHub & Polish (~40 hours)
Packages the project for open-source release.

**Run:**
```bash
./scripts/run_phase5.sh
```

**You'll get:**
- Docker containers built
- Full documentation
- GitHub repository ready

---

## Quick Commands Reference

### Build Workspace
```bash
cd ~/martian_swarm_quantum/ros2_ws
colcon build --symlink-install
```

### Launch Full Simulation
```bash
cd ~/martian_swarm_quantum
./scripts/launch_simulation.sh --rovers=5
```

### Run Docker Stack
```bash
cd ~/martian_swarm_quantum/docker
docker-compose up
```

### Run Experiments Only
```bash
cd ~/martian_swarm_quantum
python3 run_experiments.py
```

---

## Common Tasks

### Check ROS 2 Topics
```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

### Monitor Swarm Status
```bash
ros2 topic echo /swarm/status
```

### Trigger Chaos
```bash
ros2 service call /chaos/trigger_blackout std_srvs/srv/Empty {}
```

### Trigger Quantum Merge
```bash
ros2 service call /quantum/trigger_merge std_srvs/srv/Empty {}
```

---

## First Time Setup

If this is your first time:

```bash
# 1. Run the setup script
cd ~/martian_swarm_quantum
./scripts/setup_environment.sh

# 2. Read the full guide
cat docs/SETUP_GUIDE.md

# 3. Start with Phase 1
./scripts/run_phase1.sh
```

---

## Need Help?

1. **Full Setup Guide:** `docs/SETUP_GUIDE.md`
2. **Phase Guides:** `docs/PHASE_GUIDES.md`
3. **AI Assistant:** `python3 scripts/research_rabbit.py diagnostics`
4. **Bug Finder:** `python3 scripts/bug_fixer.py <file>`

---

**Good luck with your research!**
