# Fallback profiles
## What?
Fallback profiles present a way to allow general overrides for different fight 
styles. 

## Why?
If you want your spec to be simulated in e.g. `hecticaddcleave` with a
different profile than the current SimulationCraft stacked chart profile,
provide a fitting profile here.

## How?
Provide a profile via **Pull Request** or **Ticket** ([here](https://github.com/Bloodmallet/bloodytools/issues))

Files need to follow SimulationCrafts naming scheme: `T<NUMBER>_<CLASS>_<SPEC>[_<COVENANT>].simc`
E.g.:
- T27_Shaman_Elemental.simc
- T27_Shaman_Elemental_Night_Fae.simc
- T27_Warrior_Fury_Venthyr.simc

Files need to be placed in an appropriate sub-directory next to this file. Directory scheme: `<FIGHT_STYLE>/Tier<NUMBER>/`. FIGHT_STYLE needs to be in lower cases.
E.g. full file path:
- `/fallback_profiles/patchwerk/Tier27/T27_Shaman_Elemental.simc` will overwrite SimulationCrafts base profile for patchwerk and castingpatchwerk
- `/fallback_profiles/hecticaddcleave/Tier27/T27_Shaman_Elemental.simc` will overwrite SimulationCrafts base profile for hecticaddcleave
- `/fallback_profiles/hecticaddcleave/Tier27/T27_Shaman_Elemental_Night_Fae.simc` will provide a covenant specific overwrite for hecticaddcleave

## Order
Profiles are loaded in the following order. Later loads overwrite earlier ones
1. fallback covenant profiles
2. SimulationCraft covenant profiles
3. fallback baseline profile
4. SimulationCraft baseline profile for patchwerk and castingpatchwerk fight, or if no fallback was found
5. custom profile
6. the winner of the previous 3 steps overwrites the matching covenant specific profile

## Special mentions
`patchwerk` and `castingpatchwerk` fight styles will both be fueled by one directory: `patchwerk`
