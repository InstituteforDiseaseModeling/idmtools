"""
Wrapper script that runs model.py and then generates plots.

This script is meant to run within a single COMPS simulation:
1. Runs the SIR model (model.py)
2. Generates plots from the output.json
3. All outputs (output.json + plots) are in the same simulation OUTPUT directory
"""

import sys
import json
import subprocess
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def run_model():
    """Run the model.py script with parameters from command line."""
    print("="*70)
    print("STEP 1: Running SIR Model")
    print("="*70)

    # Pass all arguments to model.py
    cmd = ["python3", "sir-model-config.py"] + sys.argv[1:]

    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode != 0:
        print(f"ERROR: model.py failed with return code {result.returncode}")
        sys.exit(result.returncode)

    print("✓ Model completed successfully")
    return result.returncode


def plot_results():
    """Generate plots from output.json."""
    print("\n" + "="*70)
    print("STEP 2: Generating Plots")
    print("="*70)

    # Load results
    try:
        with open("output.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("ERROR: output.json not found!")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in output.json: {e}")
        return 1

    # Extract data
    params = results['parameters']
    summary = results['summary']
    ts = results['time_series']

    print(f"\nParameters:")
    print(f"  Beta: {params['beta']:.3f}")
    print(f"  Gamma: {params['gamma']:.3f}")
    print(f"  R0: {params['R0']:.2f}")
    print(f"  Population: {params['population']:,}")

    print(f"\nResults:")
    print(f"  Peak Infected: {summary['peak_infected']:.0f} (day {summary['peak_day']})")
    print(f"  Attack Rate: {summary['attack_rate']*100:.1f}%")

    # Create plots
    print("\nGenerating plots...")

    # Plot 1: Full time series (3 compartments)
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(ts['day'], ts['susceptible'], 'b-', linewidth=2.5, label='Susceptible', alpha=0.8)
    ax.plot(ts['day'], ts['infected'], 'r-', linewidth=2.5, label='Infected', alpha=0.8)
    ax.plot(ts['day'], ts['recovered'], 'g-', linewidth=2.5, label='Recovered', alpha=0.8)

    ax.set_xlabel('Days', fontsize=13)
    ax.set_ylabel('Number of Individuals', fontsize=13)
    ax.set_title(f'SIR Model: β={params["beta"]:.3f}, γ={params["gamma"]:.3f}, R₀={params["R0"]:.2f}',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('sir_full_timeseries.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: sir_full_timeseries.png")
    plt.close()

    # Plot 2: Infected only (zoomed)
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(ts['day'], ts['infected'], 'r-', linewidth=3)
    ax.axvline(x=summary['peak_day'], color='black', linestyle='--',
               alpha=0.5, label=f"Peak day: {summary['peak_day']}")
    ax.axhline(y=summary['peak_infected'], color='gray', linestyle='--',
               alpha=0.5, label=f"Peak: {summary['peak_infected']:.0f}")

    ax.set_xlabel('Days', fontsize=13)
    ax.set_ylabel('Number of Infected', fontsize=13)
    ax.set_title(f'Infection Curve (β={params["beta"]:.3f}, R₀={params["R0"]:.2f})',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('infected_curve.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: infected_curve.png")
    plt.close()

    # Plot 3: Summary statistics bar chart
    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ['Peak\nInfected', 'Final\nRecovered', 'Attack\nRate (%)']
    values = [
        summary['peak_infected'],
        summary['final_size'],
        summary['attack_rate'] * 100
    ]
    colors = ['red', 'green', 'orange']

    bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.0f}',
               ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Value', fontsize=13)
    ax.set_title(f'Summary Statistics (β={params["beta"]:.3f})',
                fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('summary_stats.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: summary_stats.png")
    plt.close()

    print("\n✓ All plots generated successfully")
    return 0


def main():
    """Main execution."""
    print("="*70)
    print("SIR MODEL WITH AUTOMATIC PLOTTING")
    print("="*70)

    # Step 1: Run model
    ret = run_model()
    if ret != 0:
        return ret

    # Step 2: Generate plots
    ret = plot_results()
    if ret != 0:
        return ret

    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print("\nOutput files created:")
    print("  - output.json (model results)")
    print("  - sir_full_timeseries.png (S, I, R curves)")
    print("  - infected_curve.png (infection curve)")
    print("  - summary_stats.png (statistics)")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
