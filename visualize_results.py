#!/usr/bin/env python3
"""
Paper-Ready Visualization Dashboard for Martian Swarm Quantum Results
Generates publication-quality figures for all 4 metrics
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
from datetime import datetime

# Set style for publication quality
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.figsize': (12, 8),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

RESULTS_DIR = "/home/chandan/martian_swarm_quantum/simulation_results"
OUTPUT_DIR = "/home/chandan/martian_swarm_quantum/final_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_results():
    """Load simulation results"""
    with open(f'{RESULTS_DIR}/results.json', 'r') as f:
        return json.load(f)

def create_survivability_chart(data):
    """Create survivability comparison chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['SNN\n(Neuromorphic)', 'DWA\n(Traditional)', 'TEB\n(Traditional)']
    values = [
        data['survivability']['snn_rate'] * 100,
        data['survivability']['dwa_rate'] * 100,
        data['survivability']['teb_rate'] * 100
    ]
    colors = ['#2ecc71', '#e74c3c', '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add target line
    ax.axhline(y=90, color='#3498db', linestyle='--', linewidth=2, label='90% Target')
    
    # Value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Survival Rate (%)', fontweight='bold')
    ax.set_title('1. Swarm Survivability Rate\n(The Neuromorphic Advantage)', fontweight='bold', pad=20)
    ax.set_ylim(0, 105)
    ax.legend(loc='upper right')
    
    # Add success annotation
    if data['survivability']['snn_rate'] >= 0.90:
        ax.annotate('✓ TARGET ACHIEVED', xy=(0.5, 0.95), xycoords='axes fraction',
                    fontsize=16, fontweight='bold', color='#2ecc71', ha='center')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/survivability_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/survivability_chart.png")

def create_speedup_chart(data):
    """Create quantum speedup comparison chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    speedup = data['map_stitching']['quantum_speedup']
    q_time = data['map_stitching']['quantum_time_mean']
    c_time = data['map_stitching']['classical_time_mean']
    
    categories = ['Quantum\n(QAOA)', 'Classical\n(Pose Graph)']
    times = [q_time, c_time]
    colors = ['#3498db', '#95a5a6']
    
    bars = ax.bar(categories, times, color=colors, edgecolor='black', linewidth=1.5)
    
    # Value labels
    for bar, val in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.2f} ms', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Merge Time (ms)', fontweight='bold')
    ax.set_title(f'2. Quantum Map Stitching Speed\n({speedup:.1f}x Speedup)', fontweight='bold', pad=20)
    
    # Speedup annotation
    ax.annotate(f'Quantum Advantage:\n{speedup:.1f}x faster', 
                xy=(0.5, 0.85), xycoords='axes fraction',
                fontsize=14, fontweight='bold', color='#3498db', ha='center',
                bbox=dict(boxstyle='round', facecolor='#ecf0f1', edgecolor='#3498db'))
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/speedup_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/speedup_chart.png")

def create_rmse_chart(data):
    """Create RMSE accuracy comparison chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    q_rmse = data['map_stitching']['quantum_rmse_mean'] * 100  # Convert to cm
    c_rmse = data['map_stitching']['classical_rmse_mean'] * 100
    
    categories = ['Quantum\nStitched', 'Classical\nStitched']
    values = [q_rmse, c_rmse]
    colors = ['#3498db', '#95a5a6']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Target line
    ax.axhline(y=10, color='#e74c3c', linestyle='--', linewidth=2, label='10cm Target')
    
    # Value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.2f} cm', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('RMSE (cm)', fontweight='bold')
    ax.set_title('3. Global Map Accuracy (RMSE)\n(Lower is Better)', fontweight='bold', pad=20)
    ax.set_ylim(0, 15)
    ax.legend(loc='upper right')
    
    # Status annotation
    if q_rmse < 10:
        ax.annotate('✓ TARGET MET', xy=(0.5, 0.90), xycoords='axes fraction',
                    fontsize=16, fontweight='bold', color='#2ecc71', ha='center')
    else:
        ax.annotate(f'RMSE: {q_rmse:.1f}cm', xy=(0.5, 0.90), xycoords='axes fraction',
                    fontsize=14, color='#f39c12', ha='center')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/rmse_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/rmse_chart.png")

def create_power_chart(data):
    """Create power efficiency comparison chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    snn_power = data['power']['snn_mean_power'] / 1000  # Convert to W
    global_power = data['power']['global_slam_mean_power'] / 1000
    
    categories = ['SNN\n(Neuromorphic)', 'Global SLAM\n(Traditional)']
    values = [snn_power, global_power]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    
    # Value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f} W', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Savings annotation
    savings = data['power']['energy_savings_percent']
    ax.annotate(f'Energy Savings:\n{savings:.0f}%', 
                xy=(0.5, 0.85), xycoords='axes fraction',
                fontsize=14, fontweight='bold', color='#2ecc71', ha='center',
                bbox=dict(boxstyle='round', facecolor='#ecf0f1', edgecolor='#2ecc71'))
    
    ax.set_ylabel('Power Consumption (W)', fontweight='bold')
    ax.set_title('4. Edge Power Efficiency\n(Neuromorphic vs Global SLAM)', fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/power_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/power_chart.png")

def create_summary_dashboard(data):
    """Create comprehensive summary dashboard"""
    fig = plt.figure(figsize=(16, 12))
    
    # Create grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # 1. Survivability (top-left)
    ax1 = fig.add_subplot(gs[0, 0])
    categories = ['SNN', 'DWA', 'TEB']
    values = [data['survivability']['snn_rate'] * 100,
              data['survivability']['dwa_rate'] * 100,
              data['survivability']['teb_rate'] * 100]
    colors = ['#2ecc71', '#e74c3c', '#e74c3c']
    bars1 = ax1.bar(categories, values, color=colors, edgecolor='black')
    ax1.axhline(y=90, color='#3498db', linestyle='--', linewidth=2)
    ax1.set_ylabel('Survival Rate (%)')
    ax1.set_title('1. Survivability Rate', fontweight='bold')
    ax1.set_ylim(0, 105)
    for bar, val in zip(bars1, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.0f}%', ha='center', fontsize=11, fontweight='bold')
    
    # 2. Speedup (top-right)
    ax2 = fig.add_subplot(gs[0, 1])
    cats = ['Quantum', 'Classical']
    times = [data['map_stitching']['quantum_time_mean'],
             data['map_stitching']['classical_time_mean']]
    colors2 = ['#3498db', '#95a5a6']
    bars2 = ax2.bar(cats, times, color=colors2, edgecolor='black')
    ax2.set_ylabel('Merge Time (ms)')
    ax2.set_title(f'2. Map Stitching Speed ({data["map_stitching"]["quantum_speedup"]:.0f}x faster)', fontweight='bold')
    for bar, val in zip(bars2, times):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}ms', ha='center', fontsize=11, fontweight='bold')
    
    # 3. RMSE (bottom-left)
    ax3 = fig.add_subplot(gs[1, 0])
    rmse_vals = [data['map_stitching']['quantum_rmse_mean'] * 100,
                 data['map_stitching']['classical_rmse_mean'] * 100]
    bars3 = ax3.bar(['Quantum', 'Classical'], rmse_vals, color=['#3498db', '#95a5a6'], edgecolor='black')
    ax3.axhline(y=10, color='#e74c3c', linestyle='--', linewidth=2, label='10cm Target')
    ax3.set_ylabel('RMSE (cm)')
    ax3.set_title('3. Map Accuracy (RMSE)', fontweight='bold')
    ax3.legend()
    for bar, val in zip(bars3, rmse_vals):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{val:.1f}cm', ha='center', fontsize=11, fontweight='bold')
    
    # 4. Power (bottom-right)
    ax4 = fig.add_subplot(gs[1, 1])
    power_vals = [data['power']['snn_mean_power'] / 1000,
                  data['power']['global_slam_mean_power'] / 1000]
    bars4 = ax4.bar(['SNN', 'Global SLAM'], power_vals, color=['#2ecc71', '#e74c3c'], edgecolor='black')
    ax4.set_ylabel('Power (W)')
    ax4.set_title(f'4. Power Efficiency ({data["power"]["energy_savings_percent"]:.0f}% savings)', fontweight='bold')
    for bar, val in zip(bars4, power_vals):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.0f}W', ha='center', fontsize=11, fontweight='bold')
    
    # Main title
    fig.suptitle('Martian Swarm Quantum - Paper Results Dashboard', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Footer
    fig.text(0.5, 0.02, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Martian Swarm Quantum Simulation',
             ha='center', fontsize=10, style='italic')
    
    plt.savefig(f'{OUTPUT_DIR}/dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/dashboard.png")

def create_trial_comparison(results):
    """Create trial-by-trial comparison"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    trials = [r['trial_id'] for r in results['trials']]
    
    # Survival rates
    ax = axes[0, 0]
    snn_rates = [r['snn_survivors'] / 10 * 100 for r in results['trials']]
    dwa_rates = [r['dwa_survivors'] / 10 * 100 for r in results['trials']]
    ax.plot(trials, snn_rates, 'go-', label='SNN', linewidth=2, markersize=6)
    ax.plot(trials, dwa_rates, 'ro-', label='DWA', linewidth=1, markersize=4, alpha=0.7)
    ax.axhline(y=90, color='#3498db', linestyle='--', linewidth=2, label='90% Target')
    ax.set_xlabel('Trial')
    ax.set_ylabel('Survival Rate (%)')
    ax.set_title('Survival Rate by Trial', fontweight='bold')
    ax.legend()
    ax.set_ylim(0, 105)
    
    # Merge times
    ax = axes[0, 1]
    q_times = [r['quantum_time'] * 1000 for r in results['trials']]
    c_times = [r['classical_time'] * 1000 for r in results['trials']]
    ax.bar(range(len(trials)), q_times, label='Quantum', alpha=0.8, color='#3498db')
    ax.plot(range(len(trials)), c_times, 'r--', linewidth=2, label='Classical')
    ax.set_xlabel('Trial')
    ax.set_ylabel('Merge Time (ms)')
    ax.set_title('Map Stitching Time by Trial', fontweight='bold')
    ax.legend()
    
    # RMSE
    ax = axes[1, 0]
    q_rmse = [r['quantum_rmse'] * 100 for r in results['trials']]
    c_rmse = [r['classical_rmse'] * 100 for r in results['trials']]
    ax.plot(trials, q_rmse, 'b^-', label='Quantum', linewidth=2, markersize=6)
    ax.plot(trials, c_rmse, 's-', label='Classical', linewidth=1, alpha=0.7, color='#95a5a6')
    ax.axhline(y=10, color='#e74c3c', linestyle='--', linewidth=2, label='10cm Target')
    ax.set_xlabel('Trial')
    ax.set_ylabel('RMSE (cm)')
    ax.set_title('Map Accuracy by Trial', fontweight='bold')
    ax.legend()
    
    # Energy
    ax = axes[1, 1]
    snn_eng = [r['snn_energy'] / 1000 for r in results['trials']]
    global_eng = [r['global_slam_energy'] / 1000 for r in results['trials']]
    x = np.arange(len(trials))
    width = 0.35
    ax.bar(x - width/2, snn_eng, width, label='SNN', color='#2ecc71')
    ax.bar(x + width/2, global_eng, width, label='Global SLAM', color='#e74c3c')
    ax.set_xlabel('Trial')
    ax.set_ylabel('Energy (kJ)')
    ax.set_title('Energy Consumption by Trial', fontweight='bold')
    ax.legend()
    
    fig.suptitle('Trial-by-Trial Results Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/trial_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/trial_comparison.png")

def main():
    print("="*60)
    print("  Generating Paper-Quality Visualizations")
    print("="*60)
    
    try:
        data = load_results()
        
        print("\nCreating charts...")
        create_survivability_chart(data)
        create_speedup_chart(data)
        create_rmse_chart(data)
        create_power_chart(data)
        create_summary_dashboard(data)
        create_trial_comparison(data)
        
        print("\n" + "="*60)
        print("  All visualizations saved to:")
        print(f"  {OUTPUT_DIR}")
        print("="*60)
        
        # Print summary
        print("\n📊 RESULTS SUMMARY:")
        print(f"  1. Survivability: {data['survivability']['snn_rate']*100:.1f}%")
        print(f"  2. Speedup: {data['map_stitching']['quantum_speedup']:.1f}x")
        print(f"  3. RMSE: {data['map_stitching']['quantum_rmse_mean']*100:.2f} cm")
        print(f"  4. Power Savings: {data['power']['energy_savings_percent']:.1f}%")
        
    except FileNotFoundError:
        print(f"Error: results.json not found in {RESULTS_DIR}")
        print("Please run the simulation first: python run_optimized_sim.py")

if __name__ == "__main__":
    main()
