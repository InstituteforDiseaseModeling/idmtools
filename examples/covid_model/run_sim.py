import covid_abm

do_plot = 1
do_save = 1
verbose = 0

for seed in range(100):
    sim = covid_abm.Sim()
    sim.set_seed(seed) # 4 ok, 5 ok, 6 good
    sim.run(verbose=verbose)
    sim.likelihood()
    if do_plot:
        sim.plot(do_save=f"{seed}.png")