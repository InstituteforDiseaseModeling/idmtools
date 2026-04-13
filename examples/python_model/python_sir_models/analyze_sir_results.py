# analyze_sir_results.py
import pandas as pd
import matplotlib.pyplot as plt

from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities import IAnalyzer


class SIRAnalyzer(IAnalyzer):
    def __init__(self):
        super().__init__(
            filenames=["output.json", "sir_curve.png"]
        )

    def map(self, data, simulation):
        """Extract results from each simulation."""
        results = data.get("output.json")
        if not results:
            return None

        return {
            "sim_id": str(simulation.id),
            "beta": float(simulation.tags.get("beta", 0)),
            "gamma": float(simulation.tags.get("gamma", 0)),
            "peak_infected": results["peak_infected"],
            "peak_day": results["peak_day"],
            "final_recovered": results["final_infected_total"]
        }

    def reduce(self, all_data):
        """Aggregate and visualize results."""

        rows = []
        for simulation, result in all_data.items():
            rows.append(result)

        df = pd.DataFrame(rows)
        # Create summary plot
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Peak infected vs beta
        axes[0].scatter(df["beta"], df["peak_infected"])
        axes[0].set_xlabel("Transmission Rate (β)")
        axes[0].set_ylabel("Peak Infected")
        axes[0].set_title("Peak Infections vs Transmission Rate")
        axes[0].grid(True)

        # Plot 2: Peak day vs beta
        axes[1].scatter(df["beta"], df["peak_day"])
        axes[1].set_xlabel("Transmission Rate (β)")
        axes[1].set_ylabel("Peak Day")
        axes[1].set_title("Timing of Peak vs Transmission Rate")
        axes[1].grid(True)

        plt.tight_layout()
        plt.savefig("sir_analysis.png", dpi=150)
        plt.close()

        print("\nSummary Statistics:")
        print(df.describe())

        return df


if __name__ == "__main__":
    # Set the platform where you want to run your analysis
    with Platform('SlurmStage') as platform:
        # Set the experiment you want to analyze
        exp_id = 'f9f8e80c-4a09-f111-9318-f0921c167864'  # comps exp id

        # Initialize the analyser class with the name of file to save to and start the analysis
        analyzers = [SIRAnalyzer()]

        # Specify the id Type, in this case an Experiment
        manager = AnalyzeManager(ids=[(exp_id, ItemType.EXPERIMENT)], analyzers=analyzers)
        manager.analyze()
