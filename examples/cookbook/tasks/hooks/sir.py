from argparse import ArgumentParser
from logging import getLogger, INFO, basicConfig

from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
basicConfig(level=INFO)
logger = getLogger(__name__)


def run_simulation(N, I0, R0, beta, gamma, days):
    # Everyone else, S0, is susceptible to infection initially.
    S0 = N - I0 - R0
    # A grid of time points (in days)
    t = np.linspace(0, days, days)

    # The SIR model differential equations.
    def deriv(y, t, N, beta, gamma):
        S, I, R = y
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    # Initial conditions vector
    y0 = S0, I0, R0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T

    # Plot the data on three separate curves for S(t), I(t) and R(t)
    fig = plt.figure(facecolor='w')
    ax = fig.add_subplot(111, facecolor='#dddddd', axisbelow=True)
    ax.plot(t, S/1000, 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(t, I/1000, 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(t, R/1000, 'g', alpha=0.5, lw=2, label='Recovered with immunity')
    ax.set_xlabel('Time /days')
    ax.set_ylabel('Number (1000s)')
    ax.set_ylim(0, 1.2)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    fig.savefig('results.png', dpi=fig.dpi)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--N", "--total-population", default=1000, type=int, help="Total Population")
    parser.add_argument("--I0", "--initial-infected", default=1, type=int, help="Total number of initial infected")
    parser.add_argument("--R0", "--initial-recovered", default=0, type=int, help="Total number of initial recovered")
    parser.add_argument("--beta", "--contact-rate", default=0.2, type=float, help="Contact Rate")
    parser.add_argument("--gamma", "--mean-recovery-rate", default=1./10, type=float, help="Contact Rate")
    parser.add_argument("--days", default=160, help="Total Days")

    args = parser.parse_args()
    logger.info(f"Using the following args: {args}")
    run_simulation(args.N, args.I0, args.R0, args.beta, args.gamma, args.days)
