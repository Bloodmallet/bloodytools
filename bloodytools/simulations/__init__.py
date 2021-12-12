from bloodytools.simulations.simulator import SimulatorFactory
from bloodytools.simulations.race_simulator import RaceSimulator
from bloodytools.simulations.soulbind_simulator import SoulbindSimulator
from bloodytools.simulations.tier_set_simulator import TierSetSimulator

simulator_factory = SimulatorFactory()

simulator_factory.register_simulator("races", RaceSimulator)
simulator_factory.register_simulator("soulbinds", SoulbindSimulator)
simulator_factory.register_simulator("tier_set", TierSetSimulator)
