# sir_model.py
import argparse
import os
import sys
import json
import matplotlib.pyplot as plt

def sir_model(N, beta, gamma, days, initial_infected=1):
    """
    Simple SIR model implementation.

    Parameters:
    - N: Total population
    - beta: Transmission rate
    - gamma: Recovery rate
    - days: Number of days to simulate
    - initial_infected: Initial number of infected individuals
    """
    # Initialize compartments
    S = N - initial_infected
    I = initial_infected
    R = 0

    # Store time series
    S_history = [S]
    I_history = [I]
    R_history = [R]

    # Run simulation
    for day in range(days):
        # Calculate new infections and recoveries
        new_infections = beta * S * I / N
        new_recoveries = gamma * I

        # Update compartments
        S -= new_infections
        I += new_infections - new_recoveries
        R += new_recoveries

        # Store results
        S_history.append(S)
        I_history.append(I)
        R_history.append(R)

    # Save results
    results = {
        "S": S_history,
        "I": I_history,
        "R": R_history,
        "final_infected_total": R,
        "peak_infected": max(I_history),
        "peak_day": I_history.index(max(I_history))
    }

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(S_history, label="Susceptible", color="blue")
    plt.plot(I_history, label="Infected", color="red")
    plt.plot(R_history, label="Recovered", color="green")
    plt.xlabel("Days")
    plt.ylabel("Number of Individuals")
    plt.title(f"SIR Model: β={beta:.3f}, γ={gamma:.3f}")
    plt.legend()
    plt.grid(True)
    plt.savefig("sir_curve.png", dpi=150)
    plt.close()

    print(f"Simulation complete: Peak infected = {max(I_history):.0f} on day {I_history.index(max(I_history))}")

    return results

if __name__ == "__main__":
    # Read parameters from command line or config file
    if len(sys.argv) > 1:
        # Read from config file
        with open(sys.argv[1], "r") as f:
            config = json.load(f)
    else:
        # Default parameters
        config = {
            "N": 10000,
            "beta": 0.5,
            "gamma": 0.1,
            "days": 160
        }

    # Run model
    sir_model(**config)