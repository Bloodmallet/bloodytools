Bloody( tools )
![CI](https://github.com/Bloodmallet/bloodytools/actions/workflows/CI.yaml/badge.svg)
===========
<!-- These service no longer exist [![Build Status](https://travis-ci.org/Bloodmallet/bloodytools.svg?branch=dev)](https://travis-ci.org/Bloodmallet/bloodytools) [![Coverage Status](https://coveralls.io/repos/github/Bloodmallet/bloodytools/badge.svg?branch=dev)](https://coveralls.io/github/Bloodmallet/bloodytools?branch=dev) -->

> Automation tool for several different aspects of all dps and some tank specs in World of Warcraft using SimulationCraft. Ingame customization and number tuning make decision making without external help a bloody hell.

## Requirements
You need
- [SimulationCraft](http://downloads.simulationcraft.org/?C=M;O=D) ([GitHub Repository](https://github.com/simulationcraft/simc)),
- [Python 3.6](https://www.python.org/downloads/) or newer,
- [simc_support](https://github.com/Bloodmallet/simc_support) (which is handled in the requirements.txt).


## Download
Download or clone this repository next to your SimulationCraft directory.

```
├── SimulationCraft/
└── bloodytools/
    └── README.md
```

## Setup - Short
Start python environement. Install dependencies.
```sh
$ <env_name>\Scripts\active
(<env_name>)$ pip install -U -r .\requirements.txt
```

## Setup - First Timers
- [Get Git](https://gitforwindows.org/)
- [Get Python 3.6+](https://www.python.org/downloads/), pay attention to install into path (checkbox).
- [Windows] Start the Commandline or PowerShell
- [Linux] Start a Terminal
- `python --version` should return the python 3.6+ version number you installed, if it doesn't, try `python3 --version`. Use whatever (python/python3) returned the correct version in the next step
- [Create a virtual 3.6+ environment](https://docs.python.org/3/library/venv.html) inside `bloodytools` directory, `python -m venv env`
- Start the virtual env you just created
  - [Windows] `env/Scripts/activate`
  - [Linux] `source env/bin/activate`
- "(env)" should appear in front of your line
- Check python version again: `python --version`
- `python -m pip install --upgrade pip` to update the installer of extra tools
- `pip install -U -r requirements.txt`
Congratulations, you're ready to execute the command of `Getting started` in your already open Commandline/Powershell/Terminal.

## Getting started
Edit `bloodytools/settings.py` to your liking using a text editor like Notepad++. Start python environement. Start bloodytools.
```sh
$ cd ~/bloodytools
$ <env_name>/Scripts/activate
(<env_name>)$ python -m bloodytools
```

## Development
If you see a lack of features somewhere or ways to improve the quality of the code, please contact me or create an [issue](https://github.com/Bloodmallet/bloodytools/issues). You can also fork this project and create a pull request with your ideas. Please use `black` to format your code.

## Contact
Meet me in [Discord](https://discord.gg/sXfmMkm). My username is Bloodmallet(EU)#8246.

## Support the creator
If you want to support the development: [![PayPal link](https://img.shields.io/badge/PayPal-donate-blue.svg)](https://www.paypal.me/bloodmallet) [![Patreon link](https://img.shields.io/badge/Patreon-pledge-blue.svg)](https://www.patreon.com/bloodmallet)
