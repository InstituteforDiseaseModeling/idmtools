'''
Simplest possible Covasim usage example.
'''
import os
import sys

import covasim as cv

sys.path.insert(0, os.path.dirname(__file__))
import sim_to_inset

# Set the output directory path
outputs = "outputs"
if not os.path.exists(outputs):
    os.makedirs(outputs)

sim = cv.Sim()
sim.run()
sim.plot()
cv.savefig('sim.png')
sim.to_json(filename=os.path.join(outputs, "results.json"))
sim.to_excel(filename=os.path.join(outputs, "results.xlsx"))

sim_to_inset.create_insetchart(sim.to_json(tostring=False))