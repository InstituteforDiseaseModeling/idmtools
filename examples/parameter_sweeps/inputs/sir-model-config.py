"""
Simple SIR model for parameter sweep tutorial.

This model demonstrates a basic epidemiological simulation that can be
parameterized for sweeps over beta (transmission rate), gamma (recovery rate),
population size, and simulation duration.
"""

import sys
import json
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Default parameters
DEFAULTS = {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "days": 160,
    "initial_infected": 1,
    "output": "output.json"
}


def sir_model(population, beta, gamma, days, initial_infected=1):
    """
    Run a simple SIR (Susceptible-Infected-Recovered) model.

    Parameters:
    -----------
    population : int
        Total population size
    beta : float
        Transmission rate (contact rate x probability of transmission)
    gamma : float
        Recovery rate (1/infectious period)
    days : int
        Number of days to simulate
    initial_infected : int
        Initial number of infected individuals (default: 1)

    Returns:
    --------
    dict : Results including time series and summary statistics
    """
    S = population - initial_infected
    I = initial_infected
    R = 0

    time_series = {
        "day": [],
        "susceptible": [],
        "infected": [],
        "recovered": []
    }

    for day in range(days + 1):
        time_series["day"].append(day)
        time_series["susceptible"].append(S)
        time_series["infected"].append(I)
        time_series["recovered"].append(R)

        if day < days:
            new_infections = beta * S * I / population
            new_recoveries = gamma * I
            S -= new_infections
            I += new_infections - new_recoveries
            R += new_recoveries

    max_infected = max(time_series["infected"])
    peak_day = time_series["infected"].index(max_infected)
    final_size = time_series["recovered"][-1]
    attack_rate = final_size / population
    R0 = beta / gamma

    results = {
        "parameters": {
            "population": population,
            "beta": beta,
            "gamma": gamma,
            "days": days,
            "R0": R0
        },
        "summary": {
            "peak_infected": max_infected,
            "peak_day": peak_day,
            "final_size": final_size,
            "attack_rate": attack_rate,
            "total_infected": final_size
        },
        "time_series": time_series
    }

    return results


def plot_results():
    """Generate plots from output.json."""
    print("\n" + "="*70)
    print("STEP 2: Generating Plots")
    print("="*70)
    output_file = os.path.join(os.getcwd(), "output.json")
    try:
        with open(output_file, "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("ERROR: output.json not found!")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in output.json: {e}")
        return 1

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

    print("\nGenerating plots...")

    # Plot 1: Full time series
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(ts['day'], ts['susceptible'], 'b-', linewidth=2.5, label='Susceptible', alpha=0.8)
    ax.plot(ts['day'], ts['infected'], 'r-', linewidth=2.5, label='Infected', alpha=0.8)
    ax.plot(ts['day'], ts['recovered'], 'g-', linewidth=2.5, label='Recovered', alpha=0.8)
    ax.set_xlabel('Days', fontsize=13)
    ax.set_ylabel('Number of Individuals', fontsize=13)
    ax.set_title(f'SIR Model: \u03b2={params["beta"]:.3f}, \u03b3={params["gamma"]:.3f}, R\u2080={params["R0"]:.2f}',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('sir_full_timeseries.png', dpi=300, bbox_inches='tight')
    print("  \u2713 Saved: sir_full_timeseries.png")
    plt.close()

    # Plot 2: Infected only
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ts['day'], ts['infected'], 'r-', linewidth=3)
    ax.axvline(x=summary['peak_day'], color='black', linestyle='--',
               alpha=0.5, label=f"Peak day: {summary['peak_day']}")
    ax.axhline(y=summary['peak_infected'], color='gray', linestyle='--',
               alpha=0.5, label=f"Peak: {summary['peak_infected']:.0f}")
    ax.set_xlabel('Days', fontsize=13)
    ax.set_ylabel('Number of Infected', fontsize=13)
    ax.set_title(f'Infection Curve (\u03b2={params["beta"]:.3f}, R\u2080={params["R0"]:.2f})',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('infected_curve.png', dpi=300, bbox_inches='tight')
    print("  \u2713 Saved: infected_curve.png")
    plt.close()

    # Plot 3: Summary statistics
    fig, ax = plt.subplots(figsize=(8, 6))
    metrics = ['Peak\nInfected', 'Final\nRecovered', 'Attack\nRate (%)']
    values = [summary['peak_infected'], summary['final_size'], summary['attack_rate'] * 100]
    colors = ['red', 'green', 'orange']
    bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.0f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.set_ylabel('Value', fontsize=13)
    ax.set_title(f'Summary Statistics (\u03b2={params["beta"]:.3f})',
                fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('summary_stats.png', dpi=300, bbox_inches='tight')
    print("  \u2713 Saved: summary_stats.png")
    plt.close()

    print("\n\u2713 All plots generated successfully")
    return 0


def load_config(config_path="config.json"):
    """
    Load parameters from config.json, merged with defaults.

    Args:
        config_path: Path to the JSON config file

    Returns:
        dict: Merged configuration
    """
    config = DEFAULTS.copy()

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_config = json.load(f)
        config.update(user_config)
        print(f"Loaded config from {config_path}: {user_config}")
    else:
        print(f"Config file '{config_path}' not found, using defaults.")

    return config


def main():
    """Main entry point for the model."""
    config = load_config("config.json")

    population = int(config["population"])
    beta = float(config["beta"])
    gamma = float(config["gamma"])
    days = int(config["days"])
    initial_infected = int(config["initial_infected"])
    output = config["output"]

    print("=" * 60)
    print("SIR Model Simulation")
    print("=" * 60)
    print(f"Population: {population:,}")
    print(f"Beta (transmission rate): {beta:.4f}")
    print(f"Gamma (recovery rate): {gamma:.4f}")
    print(f"R0 (basic reproduction number): {beta/gamma:.2f}")
    print(f"Simulation duration: {days} days")
    print(f"Initial Infected: {initial_infected}")
    print("=" * 60)

    results = sir_model(
        population=population,
        beta=beta,
        gamma=gamma,
        days=days,
        initial_infected=initial_infected
    )

    print("\nSimulation Results:")
    print("-" * 60)
    print(f"Peak infected: {results['summary']['peak_infected']:.0f} "
          f"(on day {results['summary']['peak_day']})")
    print(f"Final epidemic size: {results['summary']['final_size']:.0f} "
          f"({results['summary']['attack_rate']*100:.1f}% of population)")
    print(f"Total infected: {results['summary']['total_infected']:.0f}")
    print("-" * 60)

    with open(output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output}")
    plot_results()

    return 0


if __name__ == "__main__":
    sys.exit(main())
