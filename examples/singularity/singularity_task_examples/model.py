"""
Simple model that reads parameters from a JSON config file
and runs a basic computation.
"""
import argparse
import json
import math
import os


def run_model(alpha, beta, **kwargs):
    """
    Run a simple model with alpha and beta parameters.

    Args:
        alpha: Learning rate / decay parameter
        beta: Growth / scaling parameter
    """
    print(f"Running model with alpha={alpha}, beta={beta}")

    # Simple example computation
    steps = 100
    results = []
    value = 1.0

    for step in range(steps):
        value = value * (1 - alpha) + beta * math.sin(step * 0.1)
        results.append({"step": step, "value": value})

    # Save results
    output_file = os.path.join(os.getcwd(), "output.json")

    with open(output_file, "w") as f:
        json.dump({
            "parameters": {"alpha": alpha, "beta": beta},
            "results": results,
            "final_value": value
        }, f, indent=2)

    print(f"Final value: {value}")
    print(f"Results saved to {output_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run model with config file")
    parser.add_argument("--config", type=str, default="config.json",
                        help="Path to JSON config file")
    args = parser.parse_args()

    # Load config
    if os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = json.load(f)
        print(f"Loaded config from {args.config}: {config}")
    else:
        config = {"alpha": 0.1, "beta": 0.2}
        print(f"Config file not found, using defaults: {config}")

    run_model(**config)
