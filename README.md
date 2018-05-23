Bloody( tools )
===========
[![Build Status](https://travis-ci.org/Bloodmallet/bloodytools.svg?branch=dev)](https://travis-ci.org/Bloodmallet/bloodytools) [![Coverage Status](https://coveralls.io/repos/github/Bloodmallet/bloodytools/badge.svg?branch=dev)](https://coveralls.io/github/Bloodmallet/bloodytools?branch=dev)

> Automation tool for several different aspects of all dps and some tank specs in World of Warcraft using SimulationCraft. Ingame customization and number tuning make decision making without external help a bloody hell.

## In developement note
This tool is still in developement but can be used to generate some data. If you want to contribute or have suggestions to automate data and representation generation, contact me.

## Requirements
You need the latest [SimulationCraft](http://downloads.simulationcraft.org/?C=M;O=D) version ([GitHub Repository](https://github.com/simulationcraft/simc)), [Python 3.6](https://www.python.org/downloads/) or newer and the module [simc_support](https://github.com/Bloodmallet/simc_support), which is handled in the requirements.txt.

## Download
Download or clone this repository into the SimulationCraft directory. `simulationcraft\bloodytools`

## Setup - Short
Start python environement. Install dependencies.
```sh
$ <env_name>\Scripts\active
(<env_name>)$ pip install -U -r .\requirements.txt
```

## Setup - First Timers
 - [Get Git](https://gitforwindows.org/)
 - [Get Python 3.6](https://www.python.org/downloads/), pay attention to install into path (checkbox).
 - [Windows] Start the Commandline or PowerShell
 - [Linux] Start a Terminal
 - `python --version` should return the python 3.6 version number you installed, if it doesn't, try `python3 --version`. Use whatever (python/python3) returned the correct version in the next step
 - [Create a virtual 3.6 environment](https://docs.python.org/3/library/venv.html) inside `bloodytools` directory (you might need to start the commandline on windows as administrator to do so), `python3 -m venv env`
 - Start the virtual env you just created
 - [Windows] `env/Scripts/activate`
 - [Linux] `source env/bin/activate`
 - "(env)" should appear in front of your line
 - Check python version again: `python --version`
 - `python -m pip install --upgrade pip` to update the installer of extra tools
 - `pip install -r requirements.txt`
Congratulations, you're ready to execute the command of `Getting started` in your already open Commandline/Powershell/Terminal.

## Getting started
Edit settings.py to your liking using a text editor like Notepad++. Start python environement. Start bloodytools.
```sh
(<env_name>)$ python bloodytools.py
```

## Development
If you see a lack of features somewhere or ways to improve the quality of the code, please contact me or create an [issue](https://github.com/Bloodmallet/bloodytools/issues).

## Contact
Meet me in [Discord](https://discord.gg/tFR2uvK). There is a channel #bloodmallet. My username is Bloodmallet(EU)#8246.

## Support the creator
If you want to support the developement: [![PayPal link](https://img.shields.io/badge/PayPal-donate-blue.svg)](https://www.paypal.me/bloodmallet) [![Patreon link](https://img.shields.io/badge/Patreon-pledge-blue.svg)](https://www.patreon.com/bloodmallet)
