# Martian Swarm Quantum - Phase-by-Phase Running Guides

**Total Project Time: ~300-350 hours (2-3 months full-time)**

This document contains detailed instructions for running each phase of the project.

---

## Phase 1: Environment & Storm (~40 hours)

### Objective
Build the Gazebo Mars world and MATLAB dust storm controller.

### What You'll Build
1. Martian lava tube environment in Gazebo
2. Dynamic dust storm simulation
3. ROS 2 integration for storm control
4. Sensor blinding effects (vision + LiDAR)

### Prerequisites
- [ ] Ubuntu 22.04 LTS installed
- [ ] ROS 2 Humble installed
- [ ] Gazebo Fortress installed
- [ ] MATLAB installed (with Robotics Toolbox)

### Files to Work With
```
gazebo_worlds/worlds/martian_lava_tube.world
matlab_scripts/dust_storm_controller.m
ros2_ws/src/swarm_control/ (partial - for ROS integration)
```

### Running Phase 1

**Step 1: Verify Gazebo World**
```bash
cd ~/martian_swarm_quantum
ls -la gazebo_worlds/worlds/martian_lava_tube.world
```

**Step 2: Launch Gazebo**
```bash
export GAZEBO_MODEL_PATH=~/martian_swarm_quantum/gazebo_worlds/models:$GAZEBO_MODEL_PATH
gz sim gazebo_worlds/worlds/martian_lava_tube.world
```

**Step 3: Open MATLAB**
```bash
matlab &
```

**Step 4: Run Dust Storm Controller in MATLAB**
```matlab
cd ~/martian_swarm_quantum/matlab_scripts
DustStormController
```

**Step 5: Test ROS 2 Integration**
```bash
# In another terminal
source /opt/ros/humble/setup.bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash

# Check topics
ros2 topic list | grep mars

# Should see:
# /mars_environment/dust_intensity
# /mars_environment/vision_blinding
# /mars_environment/lidar_blinding
# /mars_environment/storm_status
```

### Success Criteria
- [ ] Gazebo world loads with Martian terrain
- [ ] Dust particles visible in simulation
- [ ] MATLAB GUI shows storm controls
- [ ] ROS 2 topics publishing storm data
- [ ] Vision/LiDAR blinding works

### Common Issues
1. **Gazebo crashes**: Increase shared memory
   ```bash
   sudo sh -c 'echo " tmpfs /dev/shm tmpfs defaults,size=2g 0 0 " >> /etc/fstab'
   ```
2. **MATLAB can't find ROS**: Source MATLAB ROS package
   ```matlab
   rosinit
   ```

### Expected Output
```
Storm Status: ACTIVE
Dust Intensity: 0.75
Vision Blinding: 60%
LiDAR Degradation: 23%
```

---

## Phase 2: SNN Swarm Setup (~80 hours)

### Objective
Connect neuromorphic navigation algorithms to ROS 2 rovers.

### What You'll Build
1. 5-10 configurable rovers in Gazebo
2. SNN-based obstacle avoidance
3. Swarm coordination protocol
4. Ant-pheromone inspired navigation

### Prerequisites
- [ ] Phase 1 complete
- [ ] SNN controller (`ros2_ws/src/snn_controller/`)
- [ ] Swarm control (`ros2_ws/src/swarm_control/`)

### Files to Work With
```
ros2_ws/src/snn_controller/snn_controller/snn_node.py
ros2_ws/src/swarm_control/swarm_control/swarm_node.py
ros2_ws/src/swarm_control/launch/mars_swarm.launch.py
```

### Running Phase 2

**Step 1: Build Workspace**
```bash
cd ~/martian_swarm_quantum/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

**Step 2: Launch Swarm**
```bash
source install/setup.bash
ros2 launch swarm_control mars_swarm.launch.py num_rovers:=5
```

**Step 3: Verify Rover Spawning**
```bash
# In another terminal
ros2 topic list

# Should see:
# /rover_0/cmd_vel
# /rover_1/cmd_vel
# /rover_2/cmd_vel
# /rover_3/cmd_vel
# /rover_4/cmd_vel
# /swarm/status
# /swarm/topology
```

**Step 4: Run SNN Controller**
```bash
ros2 run snn_controller snn_node
```

**Step 5: Test Obstacle Avoidance**
```bash
# Place obstacle in Gazebo
# Watch rovers navigate around it
ros2 topic echo /snn/avoidance_direction
```

### Success Criteria
- [ ] All rovers spawn in formation
- [ ] SNN obstacle detection active
- [ ] Rovers avoid obstacles autonomously
- [ ] Mesh topology forms correctly
- [ ] Swarm coordination working

### Common Issues
1. **Rovers don't spawn**: Check Gazebo plugins
   ```bash
   gz service -l | grep spawn
   ```
2. **SNN not responding**: Check LiDAR topic
   ```bash
   ros2 topic echo /scan
   ```

### Expected Output
```
[INFO] [swarm_control]: Swarm Control initialized with 5 rovers
[INFO] [swarm_control]: Spawned rover_0 at (-10.0, -30.0)
[INFO] [swarm_control]: Spawned rover_1 at (-5.0, -30.0)
...
[INFO] [snn_controller]: SNN Controller initialized
[INFO] [snn_controller]: Architecture: 8 -> 16 -> 8
```

---

## Phase 3: Blackout Stress Test (~40 hours)

### Objective
Test rover resilience under communication failures.

### What You'll Build
1. Chaos Monkey node
2. Random mesh link severing
3. Complete blackout simulation
4. Survival mode activation

### Prerequisites
- [ ] Phase 2 complete
- [ ] Chaos monkey (`ros2_ws/src/chaos_monkey/`)

### Files to Work With
```
ros2_ws/src/chaos_monkey/chaos_monkey/chaos_node.py
```

### Running Phase 3

**Step 1: Start Chaos Monkey**
```bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run chaos_monkey chaos_node
```

**Step 2: Monitor Link Status**
```bash
# In another terminal
ros2 topic echo /chaos/link_status
```

**Step 3: Trigger Manual Blackout**
```bash
ros2 service call /chaos/trigger_blackout std_srvs/srv/Empty {}
```

**Step 4: Observe Survival Mode**
```bash
ros2 topic echo /chaos/survival_mode
```

**Step 5: End Blackout**
```bash
ros2 service call /chaos/end_blackout std_srvs/srv/Empty {}
```

### Success Criteria
- [ ] Chaos monkey runs without errors
- [ ] Link failures detected and logged
- [ ] Blackout triggers survival mode
- [ ] Rovers navigate autonomously
- [ ] Recovery after blackout

### Common Issues
1. **Blackout doesn't trigger**: Check parameters
   ```bash
   ros2 param get /chaos_monkey auto_trigger
   ```
2. **Mesh doesn't restore**: Check comm_range setting

### Expected Output
```
[WARN] [chaos_monkey]: BLACKOUT STARTED - Type: instant
[WARN] [chaos_monkey]: Duration: 120 seconds
[WARN] [chaos_monkey]: Link failure: rover_0 <-> rover_1
[WARN] [chaos_monkey]: rover_2 is now ISOLATED!
[INFO] [chaos_monkey]: BLACKOUT ENDED - Communications restored
```

---

## Phase 4: Quantum Map Recovery (~150 hours)

### Objective
Implement quantum-optimized map merging algorithm.

### What You'll Build
1. Map fragment collection from rovers
2. QUBO formulation for NP-hard problem
3. Google Cirq quantum integration
4. Simulated annealing fallback

### Prerequisites
- [ ] Phase 3 complete
- [ ] Google Cirq installed
- [ ] Quantum node (`ros2_ws/src/quantum_map_merge/`)

### Files to Work With
```
ros2_ws/src/quantum_map_merge/quantum_map_merge/quantum_node.py
scripts/quantum_optimizer.py (if separate)
```

### Running Phase 4

**Step 1: Install Cirq**
```bash
pip3 install cirq cirq-core
```

**Step 2: Verify Cirq Installation**
```bash
python3 -c "import cirq; print(cirq.__version__)"
```

**Step 3: Start Quantum Node**
```bash
source ~/martian_swarm_quantum/ros2_ws/install/setup.bash
ros2 run quantum_map_merge quantum_node
```

**Step 4: Collect Map Fragments**
```bash
# Simulate rover map data
ros2 topic pub /swarm/map_fragment std_msgs/String "{data: '{\"rover_id\": 0, \"timestamp\": 1234567890}'}"
```

**Step 5: Trigger Merge**
```bash
ros2 service call /quantum/trigger_merge std_srvs/srv/Empty {}
```

**Step 6: View Results**
```bash
ros2 topic echo /quantum/merged_map
ros2 topic echo /quantum/result
```

### Success Criteria
- [ ] QUBO matrix created correctly
- [ ] Cirq quantum circuit runs
- [ ] Map fragments collected
- [ ] Merged map published
- [ ] Fallback solver works if Cirq fails

### Common Issues
1. **Cirq import fails**: Reinstall
   ```bash
   pip3 install --upgrade cirq
   ```
2. **Merge takes too long**: Reduce fragment count
   ```bash
   ros2 param set /quantum_map_merge fragment_timeout 30.0
   ```

### Expected Output
```
[INFO] [quantum_map_merge]: EXECUTING QUANTUM MAP MERGE
[INFO] [quantum_map_merge]: Step 1: Creating QUBO formulation
[INFO] [quantum_map_merge]: QUBO size: 20x20
[INFO] [quantum_map_merge]: Step 2: Running quantum optimization
[INFO] [quantum_map_merge]: Optimization complete - Cost: -2.77
[INFO] [quantum_map_merge]: QUANTUM MAP MERGE COMPLETE
```

---

## Phase 5: GitHub & Polish (~40 hours)

### Objective
Package for open-source release.

### What You'll Build
1. Docker containers
2. Complete documentation
3. Integration tests
4. GitHub repository

### Prerequisites
- [ ] Phases 1-4 complete
- [ ] Docker installed
- [ ] GitHub account

### Files to Work With
```
docker/Dockerfile.ros2
docker/Dockerfile.gazebo
docker/Dockerfile.quantum
docker/docker-compose.yml
```

### Running Phase 5

**Step 1: Build Docker Containers**
```bash
cd ~/martian_swarm_quantum/docker
docker-compose build
```

**Step 2: Test Full Stack**
```bash
docker-compose up
```

**Step 3: Run Integration Tests**
```bash
./scripts/run_integration_tests.sh
```

**Step 4: Create GitHub Release**
```bash
git add .
git commit -m "Martian Swarm Quantum - Complete Project"
git tag v1.0.0
git push origin main --tags
```

### Success Criteria
- [ ] Docker containers build successfully
- [ ] Full stack runs in Docker
- [ ] All tests pass
- [ ] Documentation complete
- [ ] GitHub repository ready

### Expected Output
```
Building docker/ros2 ... done
Building docker/gazebo ... done
Building docker/quantum ... done
Creating network martian_swarm_default ... done
Starting ros2 ... done
Starting gazebo ... done
Starting quantum ... done
[INFO] All containers running successfully
```

---

## Running the Complete Project

### Option 1: Full Docker Stack (Recommended)

```bash
cd ~/martian_swarm_quantum/docker
docker-compose up
```

### Option 2: Native with Launch Script

```bash
cd ~/martian_swarm_quantum
./scripts/launch_simulation.sh --rovers=5
```

### Option 3: Individual Components

```bash
# Terminal 1: Gazebo
gz sim gazebo_worlds/worlds/martian_lava_tube.world

# Terminal 2: Swarm
ros2 run swarm_control swarm_node

# Terminal 3: Chaos
ros2 run chaos_monkey chaos_node

# Terminal 4: SNN
ros2 run snn_controller snn_node

# Terminal 5: Quantum
ros2 run quantum_map_merge quantum_node
```

### Option 4: Run Experiments Only

```bash
cd ~/martian_swarm_quantum
python3 run_experiments.py
```

---

## Progress Tracking

Use the results folder to track progress:

```bash
ls -la ~/martian_swarm_quantum/results/
```

Each experiment run creates:
- `swarm_control_results.json`
- `chaos_monkey_results.json`
- `quantum_map_merge_results.json`
- `snn_controller_results.json`
- `experiment_summary.json`

---

## Need Help?

1. Run diagnostics:
   ```bash
   python3 scripts/research_rabbit.py diagnostics
   ```

2. Check documentation:
   ```bash
   cat docs/SETUP_GUIDE.md
   cat docs/TROUBLESHOOTING.md
   ```

3. Ask for help with specific errors

---

**Good luck with your groundbreaking research!**
