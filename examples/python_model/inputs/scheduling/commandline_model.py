import sys
import time


def test_sweep(pop_size=10000, pop_infected=10, n_days=120, rand_seed=1, pop_type='hybrid'):
    pars = {
        "pop_size": pop_size,  # Population size
        "pop_infected": pop_infected,  # Number of initial infections
        "n_days": n_days,  # Number of days to simulate
        "rand_seed": rand_seed,  # Random seed
        "pop_type": pop_type,  # Population to use -- "hybrid" is random with household, school,and work structure
    }
    print(pars)


if __name__ == "__main__":
    pop_size= sys.argv[1]
    pop_infected = sys.argv[2]
    n_days = sys.argv[3]
    rand_seed = sys.argv[4]

    test_sweep(pop_size=pop_size, pop_infected=pop_infected, n_days=n_days, rand_seed=rand_seed, pop_type='hybrid')