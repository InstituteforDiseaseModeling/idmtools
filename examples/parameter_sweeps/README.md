<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Parameter Sweeps Tutorial Examples](#parameter-sweeps-tutorial-examples)
  - [Files](#files)
  - [Quick Start](#quick-start)
    - [1. Install idmtools](#1-install-idmtools)
    - [2. Run the Simple Sweep Example](#2-run-the-simple-sweep-example)
    - [3. Test the Model Directly](#3-test-the-model-directly)
  - [Example Output](#example-output)
  - [Model Parameters](#model-parameters)
    - [Understanding Beta and Gamma](#understanding-beta-and-gamma)
  - [Output Format](#output-format)
  - [Analyzing Results](#analyzing-results)
  - [Next Steps](#next-steps)
  - [Related Examples](#related-examples)
  - [Troubleshooting](#troubleshooting)
    - [Model doesn't run](#model-doesnt-run)
    - [No output files](#no-output-files)
    - [Import errors](#import-errors)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Parameter Sweeps Tutorial Examples

This directory contains working examples for the Parameter Sweeps Tutorial.

## Files

- **model.py** - Simple SIR (Susceptible-Infected-Recovered) epidemiological model
- **simple_sweep.py** - Basic one-dimensional parameter sweep example

## Quick Start

### 1. Install idmtools

```bash
pip install idmtools[full]
```

### 2. Run the Simple Sweep Example

```bash
cd examples/tutorials/parameter_sweeps
python simple_sweep.py
```

This will:
- Create 9 simulations (one for each beta value: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
- Run them locally on your machine
- Save results to the idmtools working directory

### 3. Test the Model Directly

You can also run the model directly to see how it works:

```bash
# With default parameters
inputs/sir-model-config.py

# With custom parameters
python inputs/sir-model-config.py --population 50000 --beta 0.7 --gamma 0.1 --days 200
python inputs/sir-model-config.py --config config.json

# View help
python sir-model-config.py --help
```

## Example Output

When you run `sweep_with_analysis.py`, you'll see output like:

```
Created 9 simulations
Beta values: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
Fixed parameters: gamma=0.1, population=10000, days=160

Running experiment...
Experiment ID: abc123-def456...
Status: Succeeded
Succeeded: 9/9

Results directory: /path/to/results
```

## Model Parameters

The SIR model accepts the following parameters:

- **population** (int): Total population size (default: 10,000)
- **beta** (float): Transmission rate - contact rate × probability of transmission (default: 0.5)
- **gamma** (float): Recovery rate - 1/infectious period (default: 0.1)
- **days** (int): Number of days to simulate (default: 160)

### Understanding Beta and Gamma

- **Beta (β)**: Higher values mean faster disease spread
  - β = 0.3: Moderate spread (e.g., with interventions)
  - β = 0.5: Typical flu-like spread
  - β = 0.9: Rapid spread (e.g., highly infectious disease)

- **Gamma (γ)**: Higher values mean faster recovery
  - γ = 0.1: 10-day infectious period (1/γ = 10)
  - γ = 0.2: 5-day infectious period

- **R0** (Basic Reproduction Number): R0 = β/γ
  - R0 < 1: Epidemic dies out
  - R0 = 1: Endemic equilibrium
  - R0 > 1: Epidemic spreads

## Output Format

Each simulation creates an `output.json` file with:

```json
{
  "parameters": {
    "population": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "days": 160,
    "R0": 5.0
  },
  "summary": {
    "peak_infected": 1234.5,
    "peak_day": 45,
    "final_size": 8567.3,
    "attack_rate": 0.857,
    "total_infected": 8567.3
  },
  "time_series": {
    "day": [0, 1, 2, ...],
    "susceptible": [9999, 9998, ...],
    "infected": [1, 2, ...],
    "recovered": [0, 0, ...]
  }
}
```

## Analyzing Results

After running the sweep, you can analyze the results:

```python
import json
import os
from pathlib import Path

# Get experiment directory
exp_dir = Path("/path/to/experiment")  # From output above

# Collect results
results = []
for sim_dir in exp_dir.iterdir():
    if sim_dir.is_dir():
        output_file = sim_dir / "output.json"
        if output_file.exists():
            with open(output_file) as f:
                data = json.load(f)
                results.append({
                    "beta": data["parameters"]["beta"],
                    "R0": data["parameters"]["R0"],
                    "peak_infected": data["summary"]["peak_infected"],
                    "peak_day": data["summary"]["peak_day"],
                    "attack_rate": data["summary"]["attack_rate"]
                })

# Print summary
for r in sorted(results, key=lambda x: x["beta"]):
    print(f"Beta: {r['beta']:.1f}, R0: {r['R0']:.1f}, "
          f"Peak: {r['peak_infected']:.0f} (day {r['peak_day']}), "
          f"Attack rate: {r['attack_rate']*100:.1f}%")
```

## Next Steps

See the [Parameter Sweeps Tutorial](../../../docs/tutorials/parameter-sweeps.md) for:
- Two-dimensional sweeps
- Multi-dimensional factorial designs
- Latin Hypercube Sampling
- Adaptive sampling strategies
- Constrained parameter spaces
- Scenario-based sweeps

## Related Examples

- `grid_sweep.py` - Two-dimensional parameter grid (beta × gamma)
- `lhs_sweep.py` - Latin Hypercube Sampling for efficient space exploration
- `scenario_sweep.py` - Scenario-based parameter exploration

## Troubleshooting

### Model doesn't run
- Ensure idmtools is installed: `pip install idmtools[full]`
- Check Python version: `python --version` (requires 3.8+)

### No output files
- Check the results directory path printed by the script
- Verify simulations succeeded: Look for "Status: Succeeded" message

### Import errors
- Install required packages: `pip install idmtools-models`
