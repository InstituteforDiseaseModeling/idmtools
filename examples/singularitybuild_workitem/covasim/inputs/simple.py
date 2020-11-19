'''
Simplest possible Covasim usage example.
'''
import os

import covasim as cv

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