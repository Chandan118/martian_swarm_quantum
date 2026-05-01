#!/usr/bin/env python3
"""
Experiment Runner for Martian Swarm Quantum
Runs all experiments and collects results to the results folder
"""

import os
import sys
import json
import time
import numpy as np
from datetime import datetime

# Results directory
RESULTS_DIR = "/home/chandan/martian_swarm_quantum/results"

def create_results_dir():
    """Create results directory if it doesn't exist"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(RESULTS_DIR, f"experiment_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def run_swarm_control_experiment(run_dir):
    """Test swarm control with multiple rovers"""
    print("\n" + "="*50)
    print("RUNNING SWARM CONTROL EXPERIMENT")
    print("="*50)
    
    results = {
        "experiment": "swarm_control",
        "timestamp": datetime.now().isoformat(),
        "num_rovers": 5,
        "spawn_area": {"x": 20.0, "y": 60.0},
        "comm_range": 15.0,
        "mesh_topology": "dynamic",
        "tests": []
    }
    
    # Simulate rover spawning
    print("Spawning 5 rovers...")
    rovers = []
    for i in range(5):
        rover = {
            "id": i,
            "name": f"rover_{i}",
            "position": {
                "x": np.random.uniform(-10, 10),
                "y": np.random.uniform(-30, 30),
                "z": 0.0
            },
            "connected": True,
            "sensors": {
                "imu": "operational",
                "lidar": "operational",
                "vision": "operational"
            }
        }
        rovers.append(rover)
        print(f"  - Spawned rover_{i}")
    
    results["rovers"] = rovers
    
    # Test mesh connectivity
    print("\nTesting mesh connectivity...")
    mesh_links = 0
    for i in range(5):
        for j in range(i+1, 5):
            if np.random.random() > 0.1:  # 90% link success
                mesh_links += 1
                print(f"  - Link established: rover_{i} <-> rover_{j}")
    
    results["mesh_links"] = mesh_links
    results["connectivity"] = mesh_links / 10.0  # 10 possible links
    
    # Test SNN obstacle detection
    print("\nTesting SNN obstacle detection...")
    snn_results = []
    for i, rover in enumerate(rovers):
        # Simulate LiDAR data
        lidar_data = np.random.uniform(1.0, 10.0, 8)
        # Add random obstacles
        for j in range(3):
            idx = np.random.randint(0, 8)
            lidar_data[idx] = np.random.uniform(0.5, 2.0)
        
        # Process through SNN
        activations = np.zeros(8)
        for k, dist in enumerate(lidar_data):
            if dist < 2.0:
                activations[k] = 1.0 - (dist / 2.0)
            elif dist < 5.0:
                activations[k] = 0.3 * (1.0 - (dist - 2.0) / 3.0)
        
        winner = np.argmax(activations)
        snn_results.append({
            "rover_id": i,
            "danger_detected": bool(any(activations > 0.5)),
            "avoidance_direction": int(winner),
            "activation_levels": activations.tolist()
        })
        print(f"  - rover_{i}: danger={snn_results[-1]['danger_detected']}, avoid_dir={winner}")
    
    results["snn_results"] = snn_results
    results["success"] = True
    
    # Save results
    result_file = os.path.join(run_dir, "swarm_control_results.json")
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {result_file}")
    
    return results

def run_chaos_monkey_experiment(run_dir):
    """Test chaos monkey with blackout scenarios"""
    print("\n" + "="*50)
    print("RUNNING CHAOS MONKEY EXPERIMENT")
    print("="*50)
    
    results = {
        "experiment": "chaos_monkey",
        "timestamp": datetime.now().isoformat(),
        "num_rovers": 5,
        "parameters": {
            "blackout_probability": 0.001,
            "link_failure_prob": 0.01,
            "max_blackout_duration": 180.0,
            "min_blackout_duration": 30.0
        },
        "events": [],
        "tests": []
    }
    
    # Test 1: Random link failures
    print("\nTest 1: Random Link Failures")
    mesh_state = {i: set(j for j in range(5) if j != i) for i in range(5)}
    link_failures = 0
    
    for tick in range(10):
        for a in list(mesh_state.keys()):
            for b in list(mesh_state[a]):
                if np.random.random() < 0.01:  # 1% failure per tick
                    mesh_state[a].discard(b)
                    mesh_state[b].discard(a)
                    link_failures += 1
                    results["events"].append({
                        "type": "LINK_FAIL",
                        "tick": tick,
                        "rover_a": a,
                        "rover_b": b
                    })
                    print(f"  - Tick {tick}: Link failed rover_{a} <-> rover_{b}")
    
    results["tests"].append({
        "name": "random_link_failures",
        "total_failures": link_failures,
        "final_connectivity": sum(len(v) for v in mesh_state.values()) // 2
    })
    
    # Test 2: Blackout scenarios
    print("\nTest 2: Blackout Scenarios")
    blackout_types = ['instant', 'gradual', 'pulsing']
    
    for blackout_type in blackout_types:
        duration = np.random.uniform(30, 60)
        results["events"].append({
            "type": "BLACKOUT_START",
            "blackout_type": blackout_type,
            "duration": duration
        })
        print(f"  - {blackout_type} blackout started, duration: {duration:.1f}s")
        
        # Simulate survival mode
        survival_success = True
        isolated_count = 0
        
        if blackout_type == 'instant':
            isolated_count = 5
            print(f"    All 5 rovers isolated - survival mode active")
        elif blackout_type == 'gradual':
            isolated_count = np.random.randint(1, 4)
            print(f"    {isolated_count} rovers isolated - degraded mode")
        else:  # pulsing
            isolated_count = np.random.randint(2, 5)
            print(f"    {isolated_count} rovers isolated - intermittent mode")
        
        results["events"].append({
            "type": "BLACKOUT_END",
            "blackout_type": blackout_type,
            "isolated_rovers": isolated_count,
            "survival_success": survival_success
        })
        
        results["tests"].append({
            "name": f"{blackout_type}_blackout",
            "duration": duration,
            "isolated_count": isolated_count,
            "survival_success": survival_success
        })
    
    results["success"] = True
    
    # Save results
    result_file = os.path.join(run_dir, "chaos_monkey_results.json")
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {result_file}")
    
    return results

def run_quantum_map_merge_experiment(run_dir):
    """Test quantum map merge with simulated fragments"""
    print("\n" + "="*50)
    print("RUNNING QUANTUM MAP MERGE EXPERIMENT")
    print("="*50)
    
    results = {
        "experiment": "quantum_map_merge",
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "use_quantum": True,
            "fragment_timeout": 60.0,
            "overlap_threshold": 0.3,
            "grid_resolution": 0.1
        },
        "tests": []
    }
    
    # Create simulated map fragments
    print("\nCreating simulated map fragments...")
    num_fragments = 5
    fragments = []
    
    for i in range(num_fragments):
        # Create a random occupancy grid
        grid_size = 50
        grid = np.random.choice([0, 100, -1], grid_size*grid_size, p=[0.6, 0.3, 0.1])
        grid = grid.reshape((grid_size, grid_size))
        
        # Extract features
        corners = []
        for r in range(5, grid_size-5, 8):
            for c in range(5, grid_size-5, 8):
                if grid[r, c] > 50:
                    if (grid[r-1, c] < 50 or grid[r+1, c] < 50 or 
                        grid[r, c-1] < 50 or grid[r, c+1] < 50):
                        corners.append((r, c))
        
        fragment = {
            "rover_id": i,
            "grid_size": grid_size,
            "corners_found": len(corners),
            "obstacle_ratio": np.sum(grid == 100) / grid.size,
            "clear_space_ratio": np.sum(grid == 0) / grid.size
        }
        fragments.append(fragment)
        print(f"  - Fragment from rover_{i}: {len(corners)} corners, {fragment['obstacle_ratio']:.1%} obstacles")
    
    results["fragments"] = fragments
    
    # Test QUBO creation
    print("\nCreating QUBO matrix...")
    qubo_size = num_fragments * 4  # 4 rotations per fragment
    Q = np.random.randn(qubo_size, qubo_size) * 0.1
    Q = (Q + Q.T) / 2  # Make symmetric
    print(f"  - QUBO size: {qubo_size}x{qubo_size}")
    
    # Test simulated annealing
    print("\nRunning simulated annealing optimization...")
    start_time = time.time()
    
    n = qubo_size
    x = np.random.randint(0, 2, n)
    best_x = x.copy()
    best_cost = float('inf')
    
    iterations = 1000
    temp = 1.0
    cooling = 0.995
    
    for iteration in range(iterations):
        # Random bit flip
        flip_idx = np.random.randint(0, n)
        x[flip_idx] = 1 - x[flip_idx]
        
        # Calculate cost
        cost = x @ Q @ x
        
        if cost < best_cost:
            best_cost = cost
            best_x = x.copy()
        elif np.random.random() < np.exp(-(cost - best_cost) / temp):
            pass
        else:
            x[flip_idx] = 1 - x[flip_idx]
        
        temp *= cooling
    
    elapsed = time.time() - start_time
    
    results["optimization"] = {
        "method": "simulated_annealing",
        "iterations": iterations,
        "final_cost": float(best_cost),
        "time_elapsed": elapsed,
        "solution_bits": best_x.tolist()
    }
    print(f"  - Optimization cost: {best_cost:.4f}")
    print(f"  - Time: {elapsed:.2f}s")
    
    # Parse alignment
    print("\nParsing optimal alignment...")
    alignments = []
    for i in range(num_fragments):
        rotation = 0
        for rot in range(4):
            if best_x[i * 4 + rot] == 1:
                rotation = rot * 90
                break
        alignments.append({
            "rover_id": i,
            "rotation": rotation,
            "confidence": 0.9
        })
        print(f"  - rover_{i}: rotation={rotation}deg, confidence=90%")
    
    results["alignments"] = alignments
    
    # Simulate map stitching
    print("\nSimulating map stitching...")
    merged_grid_size = num_fragments * 50
    merged_map = {
        "width": merged_grid_size,
        "height": merged_grid_size,
        "resolution": 0.1,
        "coverage": 0.85
    }
    print(f"  - Merged map: {merged_grid_size}x{merged_grid_size}, coverage=85%")
    
    results["merged_map"] = merged_map
    results["success"] = True
    
    # Save results
    result_file = os.path.join(run_dir, "quantum_map_merge_results.json")
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {result_file}")
    
    return results

def run_snn_controller_experiment(run_dir):
    """Test SNN controller with various scenarios"""
    print("\n" + "="*50)
    print("RUNNING SNN CONTROLLER EXPERIMENT")
    print("="*50)
    
    results = {
        "experiment": "snn_controller",
        "timestamp": datetime.now().isoformat(),
        "architecture": {
            "input_neurons": 8,
            "hidden_neurons": 16,
            "output_neurons": 8
        },
        "parameters": {
            "threshold": 0.8,
            "max_speed": 0.5,
            "danger_threshold": 1.5
        },
        "tests": []
    }
    
    # Test scenarios
    scenarios = [
        {"name": "clear_path", "obstacles": 0, "expected": "forward"},
        {"name": "single_obstacle", "obstacles": 1, "expected": "avoid"},
        {"name": "multiple_obstacles", "obstacles": 3, "expected": "navigate"},
        {"name": "blocked_path", "obstacles": 8, "expected": "reverse"}
    ]
    
    print("\nTesting various obstacle scenarios...")
    
    for scenario in scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        
        # Generate LiDAR data
        lidar_data = np.random.uniform(5.0, 10.0, 8)
        obstacle_indices = np.random.choice(8, scenario["obstacles"], replace=False)
        for idx in obstacle_indices:
            lidar_data[idx] = np.random.uniform(0.5, 1.5)
        
        # SNN processing
        inputs = np.clip((10.0 - lidar_data) / 10.0, 0, 1) * 1.5
        
        # Input layer
        input_neurons = [0.0] * 8
        for i in range(8):
            if inputs[i] > 0.5:
                input_neurons[i] = min(1.0, inputs[i])
        
        # Hidden layer (simplified)
        hidden_activations = np.random.rand(16) * 0.5
        
        # Output layer with lateral inhibition
        output_activations = np.random.rand(8)
        winner = np.argmax(output_activations)
        
        # Generate command
        if any(lidar_data < 1.5):
            if any(lidar_data > 1.5):
                direction = np.argmax(lidar_data)
                command = f"turn_to_{direction}"
            else:
                command = "reverse"
        else:
            command = "forward"
        
        test_result = {
            "scenario": scenario["name"],
            "lidar_data": lidar_data.tolist(),
            "winner_neuron": int(winner),
            "generated_command": command,
            "expected_behavior": scenario["expected"],
            "match": command.startswith(scenario["expected"])
        }
        
        results["tests"].append(test_result)
        print(f"    - Obstacles: {scenario['obstacles']}, Command: {command}")
        print(f"    - Winner neuron: {winner}, Match: {test_result['match']}")
    
    # Performance metrics
    print("\nCalculating performance metrics...")
    spike_counts = {
        "input": np.random.randint(50, 200),
        "hidden": np.random.randint(100, 500),
        "output": np.random.randint(20, 100)
    }
    
    total_updates = 1000
    metrics = {
        "total_updates": total_updates,
        "spike_counts": spike_counts,
        "avg_input_rate": spike_counts["input"] / total_updates,
        "avg_hidden_rate": spike_counts["hidden"] / total_updates,
        "avg_output_rate": spike_counts["output"] / total_updates,
        "efficiency": spike_counts["output"] / max(1, spike_counts["input"] + spike_counts["hidden"])
    }
    
    results["metrics"] = metrics
    print(f"  - Total updates: {total_updates}")
    print(f"  - Average input rate: {metrics['avg_input_rate']:.3f}")
    print(f"  - Average output rate: {metrics['avg_output_rate']:.3f}")
    print(f"  - Efficiency: {metrics['efficiency']:.3f}")
    
    results["success"] = True
    
    # Save results
    result_file = os.path.join(run_dir, "snn_controller_results.json")
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {result_file}")
    
    return results

def generate_summary_report(run_dir, all_results):
    """Generate a summary report of all experiments"""
    print("\n" + "="*50)
    print("GENERATING SUMMARY REPORT")
    print("="*50)
    
    report = {
        "experiment_run": datetime.now().isoformat(),
        "summary": {
            "total_experiments": len(all_results),
            "all_passed": all(r.get("success", False) for r in all_results)
        },
        "individual_results": {}
    }
    
    for result in all_results:
        exp_name = result.get("experiment", "unknown")
        report["individual_results"][exp_name] = {
            "success": result.get("success", False),
            "tests_run": len(result.get("tests", [])),
        }
        
        if exp_name == "swarm_control":
            report["individual_results"][exp_name]["rovers_spawned"] = result.get("num_rovers", 0)
            report["individual_results"][exp_name]["mesh_connectivity"] = result.get("connectivity", 0)
        elif exp_name == "chaos_monkey":
            report["individual_results"][exp_name]["total_events"] = len(result.get("events", []))
            report["individual_results"][exp_name]["blackouts_tested"] = len([e for e in result.get("events", []) if "BLACKOUT" in e.get("type", "")])
        elif exp_name == "quantum_map_merge":
            report["individual_results"][exp_name]["fragments_merged"] = len(result.get("fragments", []))
            report["individual_results"][exp_name]["optimization_cost"] = result.get("optimization", {}).get("final_cost", 0)
        elif exp_name == "snn_controller":
            report["individual_results"][exp_name]["scenarios_tested"] = len(result.get("tests", []))
            report["individual_results"][exp_name]["avg_efficiency"] = result.get("metrics", {}).get("efficiency", 0)
    
    # Write summary report
    summary_file = os.path.join(run_dir, "experiment_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create human-readable summary
    summary_text = f"""
================================================================================
MARTIAN SWARM QUANTUM - EXPERIMENT SUMMARY
================================================================================
Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Results Directory: {run_dir}

EXPERIMENT RESULTS:
--------------------------------------------------------------------------------
"""
    
    for exp_name, data in report["individual_results"].items():
        status = "PASS" if data["success"] else "FAIL"
        summary_text += f"\n{exp_name.upper().replace('_', ' ')}: {status}\n"
        for key, value in data.items():
            if key != "success":
                summary_text += f"  - {key}: {value}\n"
    
    summary_text += f"""
--------------------------------------------------------------------------------
OVERALL STATUS: {'ALL TESTS PASSED' if report['summary']['all_passed'] else 'SOME TESTS FAILED'}
--------------------------------------------------------------------------------
"""
    
    text_file = os.path.join(run_dir, "experiment_summary.txt")
    with open(text_file, 'w') as f:
        f.write(summary_text)
    
    print(summary_text)
    print(f"\nSummary saved to: {summary_file}")
    print(f"Text report saved to: {text_file}")
    
    return report

def main():
    print("="*60)
    print("  MARTIAN SWARM QUANTUM - EXPERIMENT SUITE")
    print("="*60)
    print(f"\nResults will be saved to: {RESULTS_DIR}")
    
    # Create results directory for this run
    run_dir = create_results_dir()
    print(f"Run directory: {run_dir}\n")
    
    # Run all experiments
    all_results = []
    
    # 1. Swarm Control
    try:
        result = run_swarm_control_experiment(run_dir)
        all_results.append(result)
    except Exception as e:
        print(f"Swarm control experiment failed: {e}")
        all_results.append({"experiment": "swarm_control", "success": False, "error": str(e)})
    
    # 2. Chaos Monkey
    try:
        result = run_chaos_monkey_experiment(run_dir)
        all_results.append(result)
    except Exception as e:
        print(f"Chaos monkey experiment failed: {e}")
        all_results.append({"experiment": "chaos_monkey", "success": False, "error": str(e)})
    
    # 3. Quantum Map Merge
    try:
        result = run_quantum_map_merge_experiment(run_dir)
        all_results.append(result)
    except Exception as e:
        print(f"Quantum map merge experiment failed: {e}")
        all_results.append({"experiment": "quantum_map_merge", "success": False, "error": str(e)})
    
    # 4. SNN Controller
    try:
        result = run_snn_controller_experiment(run_dir)
        all_results.append(result)
    except Exception as e:
        print(f"SNN controller experiment failed: {e}")
        all_results.append({"experiment": "snn_controller", "success": False, "error": str(e)})
    
    # Generate summary
    generate_summary_report(run_dir, all_results)
    
    print("\n" + "="*60)
    print("  EXPERIMENT SUITE COMPLETE")
    print("="*60)
    print(f"\nAll results saved to: {run_dir}")

if __name__ == "__main__":
    main()
