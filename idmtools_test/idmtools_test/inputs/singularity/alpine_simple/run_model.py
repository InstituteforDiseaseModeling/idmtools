import argparse
from epistoch import *
from epistoch.utils.plotting import plot_sir
from scipy import stats
import matplotlib.pyplot as plt



def run_sir_model(population, num_days, r0):
    # Let's build a SIR-G model

    dist = stats.gamma(a=2, scale=10)
    # The expected time is 20 days

    SIR_general = sir_g(
        name="SIR-G-Example",
        population=population,
        num_days=num_days,
        reproductive_factor=r0,
        infectious_time_distribution=dist,
        method="loss",
    )

    # Report a summary
    report_summary(SIR_general)

    # Now plot the result
    plot_sir(SIR_general)
    plt.savefig("result.png")

    print(SIR_general["data"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", default=1000, type=int, help="Population")
    parser.add_argument("--num-days", default=230, type=int, help="Num of days")
    parser.add_argument("--r0", default=2.2, type=float, help="Reproduction Factory")

    args = parser.parse_args()
    run_sir_model(args.population, args.num_days, args.r0)
