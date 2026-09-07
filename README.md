<p align="center">
  <img src="https://github.com/fast-aircraft-design/FAST-OAD-RTA/blob/master/docs/img/FAST_OAD_logo2.jpg?raw=true" alt="FAST-OAD logo" width="600">
</p>

# FAST-OAD plugin for Regional Transport Aircraft (RTA)
[![image](https://img.shields.io/pypi/v/fast-oad-rta.svg)](https://pypi.python.org/pypi/fast-oad-rta)
[![image](https://img.shields.io/pypi/pyversions/fast-oad-rta.svg)](https://pypi.python.org/pypi/fast-oad-rta)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![tests](https://github.com/fast-aircraft-design/FAST-OAD-RTA/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/fast-aircraft-design/RTA/graph/badge.svg?token=I9Z8KXN112)](https://codecov.io/gh/fast-aircraft-design/RTA)


## Introduction

This repository furnishes a FAST-OAD plugin for the design and analysis of Regional Transport Aircraft.
The models present in this repository rely on FAST-OAD for execution, see [FAST-OAD documentation](https://fast-oad.readthedocs.io/en/stable/documentation/custom_modules/index.html).

The models are based on the [PhD thesis](https://theses.fr/2023ESAE0020) of Vincenzo Palladino. Documentation can be found in his PhD thesis.

This README file explains how to install this repository.

It is assumed that you know how to use [Git](https://git-scm.com), 
[Python](https://www.python.org) and [FAST-OAD](https://github.com/fast-aircraft-design/FAST-OAD), especially the use of [submodels](https://fast-oad.readthedocs.io/en/v1.8.2/documentation/custom_modules/add_submodels.html#submodels-in-fast-oad).


## User installation

**Important notice**: The installation of the RTA plugin will activate by default the RTA submodels. Refer to [RTA models and submodels](#rta-models-and--submodels) for the complete list of activated submodel.

For a FAST-OAD user installation (when FAST-OAD has been installed with pip), the RTA plug-in can be installed in you python environnment using:
```bash
pip install fast-oad-rta
```
or 
```bash
pip install git+https://github.com/fast-aircraft-design/RTA.git@master
```
The latter will install the latest RTA version based on github master branch.

If you are using poetry to manage your python environment, the following command will tell poetry to add RTA to your dependencies:
```bash
poetry add git+https://github.com/fast-aircraft-design/RTA.git#master
```

Once installed, the RTA models should become visible to FAST-OAD. Simply run the following command to check that new RTA models are available:
```bash
fastoad plugin_info
```

## Tutorials
Tutorials are available in `src/rta/notebooks`. For a user installation, they can be generated through command line with:
```bash
fastoad notebooks rta
```

For a developer installation, they can be simply accessed using jupyter lab:
```bash
jupyter lab
```

## RTA models and  submodels

The RTA plug-in provides four new models:
```yml
rta.aerodynamics.takeoff
rta.loop.engine_size
rta.propulsion.propeller_sizing
rta.propulsion.turboprop_sizing
```
And a new propulsion wrapper for turbopropeller:
```yml
rta.wrapper.propulsion.ML_TP_L1
```

The model ```rta.loop.engine_size``` requires the simulation of a take-off segment during the mission, which is not activated by default.

When installing this plug-in, the new RTA submodels are activated by default. 
This means that if you attempt to run a different aircraft configuration (say a single aisle SMR), you need to modify the active submodels accordingly in the configuration file.

The list of active submodels with this plugin is given below:

```yml
'service.aerodynamics.CD0.fuselage': 'rta.submodel.aerodynamics.CD0.fuselage',
'service.aerodynamics.CD0.nacelles_pylons': 'rta.submodel.aerodynamics.CD0.nacelles',
'service.aerodynamics.CD0.sum': 'rta.submodel.aerodynamics.CD0.sum',
'service.aerodynamics.CD0.wing': 'rta.submodel.aerodynamics.CD0.wing',
'service.aerodynamics.induced_drag_coefficient': 'rta.submodel.aerodynamics.induced_drag_coefficient.legacy',
'service.geometry.fuselage.basic': 'rta.submodel.geometry.fuselage.basic',
'service.geometry.fuselage.with_cabin_sizing': 'rta.submodel.geometry.fuselage.with_cabin_sizing',
'service.geometry.nacelle_and_pylon': 'rta.submodel.geometry.nacelles',
'service.geometry.wing': 'rta.submodel.geometry.wing',
'service.weight.cg': 'rta.submodel.weight.cg.legacy',
'service.cg.wing.control_surfaces': 'rta.submodel.cg.wing.control_surfaces.legacy',
'service.cg.others': 'rta.submodel.weight.cg.others.legacy',
'service.cg.global': 'rta.submodel.weight.cg.global.legacy',
'service.cg.propulsion': 'rta.submodel.weight.cg.propulsion',
'service.mass.airframe.wing': 'rta.submodel.weight.mass.airframe.wing',
'service.mass.airframe.nacelles': 'rta.submodel.weight.mass.airframe.nacelle',
'service.mass.airframe': 'rta.submodel.weight.mass.airframe.legacy',
'service.mass.propulsion': 'rta.submodel.weight.mass.propulsion.legacy',
'service.mass.systems': 'rta.submodel.weight.mass.system.legacy',
'service.mass.furniture': 'rta.submodel.weight.mass.furniture.legacy',
'service.mass.owe': 'rta.weight.owe.legacy'
```

## Developer installation

This repository is designed to use [Poetry](https://python-poetry.org) (version 2.0.0 or above)
for managing the development environment.
Instructions below assume you have it already installed. You may adapt them if you don't 
want to use Poetry.

It is strongly recommended that you install RTA in a dedicated Python environment.

After cloning the repository, launch the installation by typing in your terminal:
```bash
poetry install
```
This will install all defined dependencies in your environment.

### Setup pre-commit
Simply run in your terminal:
```bash
pre-commit install
```

### Pytest
[Pytest](https://docs.pytest.org/) is recommended for writing tests. The development environment
is set with code coverage tools.

**Pytest and its companions are configured in `/pyproject.toml` file.**

It is recommended to have unit tests in `tests` folders next to tested code.
Other kind of tests (integration, non-regression) should be in the `/tests` folder

Unit tests will be launched with simply:
```bash
pytest
```

Other tests will be launched with
```bash
pytest tests
```

### Ruff
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
checks/corrects code style and automates the code formatting.

Kudos to [Black](https://black.readthedocs.io/en/stable) and 
[Flake8](https://flake8.pycqa.org/) that are very good tools. Yet, for a fresh start,
Ruff seems the way to go, since it does the same job as these two, only much faster.

**Ruff is configured in `/pyproject.toml` file.**

Coupled with pre-commit and/or integrated with your IDE, it
automates all the code formatting.

_**Note to PyCharm users**: there is a [ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff)._
