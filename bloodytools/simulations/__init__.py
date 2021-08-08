from bloodytools.simulations.simulator import SimulatorFactory
from bloodytools.simulations.race_simulator import RaceSimulator

simulator_factory = SimulatorFactory()

simulator_factory.register_simulation("races", RaceSimulator)
