from bloodytools.simulations.simulator import SimulatorFactory
from bloodytools.simulations.race_simulation import RaceSimulator

simulator_factory = SimulatorFactory()

simulator_factory.register_simulation("races", RaceSimulator)
