import poliosim as ps
import sim_to_inset

sim = ps.Sim(pop_size=1000, n_days=30, pop_infected=100)
sim.run()
sim_to_inset.create_insetchart(sim.results)