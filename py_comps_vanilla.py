import uuid
import sys

from COMPS import Client
from COMPS.Data import Simulation, Configuration, Priority, QueryCriteria, SimulationFile
from COMPS.Data.Simulation import SimulationState

compshost = 'https://comps2.idmod.org'

Client.login(compshost)

simid = uuid.UUID('d0ea6ec8-d005-ec11-92df-f0921c167864')

print('Getting sim: {0}'.format(str(simid)))

sim = Simulation.get(simid)

print(sim)
