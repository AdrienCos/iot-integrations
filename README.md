# IoT Integrations

This repository hosts all the code used to interface the hardware devices to the IoT frameworks.

The code in the `hardware` folder contains the implementation of framework-agnostic handler classes. These classes are then used in the `hass` (for Home Assistant) and `wt` (for WebThings) to implement device that can communicate with the respective frameworks.

## Installation

* Create a new virtual environment: `virtualenv venv`
* Activate it: `source venv/bin/activate`
* Install the dependencies: `pip install -r requirements.txt`

## Usage


Each framework folder contains a `config.py` file that contains recurring configuration options.

* Create/edit the configuration file
* Make sure the hub is reachable and the framework is on
* Make sure your MQTT broker is on and reachable
* Connect your hardware devices
* Start the integration: `python $DEVICE.py`

## Implementing new devices

Each framework folder contains a `siisthing.py` file. This file implements the `SIISThing` class, which is used by every device. It contains the data structures shared by every device handler, such as an MQTT client. To implement a new device, follow these steps:

1. Create a new hardware handler in the `hardware/` folder
2. Create a new device handler in the relevant framework folder, inheriting from the `SIISThing` class and containing an instance of your hardware handler

## Working with new frameworks

Because the hardware iterfacing is decorrelated from the framework interfacing, adding support for a new framework only requires writing a class that uses this framework's API and contains an instance of the hardware handler.