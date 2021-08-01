from bloodytools.simulations.simulation import SimulationFactory
from bloodytools.simulations.race_simulation import RaceSimulation

simulation_factory = SimulationFactory()

simulation_factory.register_simulation("races", RaceSimulation)
