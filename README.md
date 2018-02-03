Bloody( tools )
===========
[![Build Status](https://travis-ci.org/Bloodmallet/bloodytools.svg?branch=dev)](https://travis-ci.org/Bloodmallet/bloodytools) [![Coverage Status](https://coveralls.io/repos/github/Bloodmallet/bloodytools/badge.svg?branch=dev)](https://coveralls.io/github/Bloodmallet/bloodytools?branch=dev)

> Automation tool for several different aspects of all dps and some tank specs in World of Warcraft using SimulationCraft.

## Requirements
You need the latest [SimulationCraft](http://downloads.simulationcraft.org/?C=M;O=D) version ([GitHub Repository](https://github.com/simulationcraft/simc)), [Python 3.5](https://www.python.org/downloads/) or newer and the module [simc_support](https://github.com/Bloodmallet/simc_support), which is handled in the requirements.txt.

## Download
Download or clone this repository into the SimulationCraft directory. `simulationcraft\bloodytools`

## Setup
Start python environement. Install dependencies.
```sh
$ <env_name>\Scripts\active
(<env_name>)$ pip install -U -r .\requirements.txt
```

`pip freeze` should return something like this: "-e git+https://github.com/Bloodmallet/simc_support.git@e806d5ca289072684c6aca5fb03ce2b44e88cc4e#egg=simc_support"

## Getting started
Edit settings.py to your liking using any text editor. Start python environement. Start bloodytools.
```sh
$ <env_name>\Scripts\active
(<env_name>)$ python .\bloodytools.py
```

## Development
If you see a lack of features somewhere or ways to improve the quality of the code, please contact me or create an [issue](https://github.com/Bloodmallet/bloodytools/issues).
