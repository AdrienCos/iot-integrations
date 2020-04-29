from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import tornado.ioloop
import random


class SIISHVAC(Thing):
    """A HVAC that logs received commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:hvac',
            'My HVAC',
            ['Thermostat'],
            'A web connected HVAC'
        )
        self.current_temp: Value = Value(20.0)
        self.add_property(
            Property(self,
                     'temperature',
                     self.current_temp,
                     metadata={
                         '@type': 'TemperatureProperty',
                         'title': 'Temperature',
                         'type': 'number',
                         'unit': 'degree celsius',
                         'description': 'The current temperature',
                         'readOnly': True,
                         'multipleOf': 0.1,
                     }))

        self.target_temp: Value = Value(18.0, self.set_target)
        self.add_property(
            Property(self,
                     'target_temperature',
                     self.target_temp,
                     metadata={
                         '@type': 'TargetTemperatureProperty',
                         'title': 'Target Temperature',
                         'type': 'number',
                         'unit': 'degree celsius',
                         'description': 'The desired temperature',
                         'readOnly': False,
                         'multipleOf': 0.1
                     }))

        self.state: Value = Value('off')
        self.add_property(
            Property(self,
                     'state',
                     self.state,
                     metadata={
                         '@type': 'HeatingCoolingMode',
                         'title': 'State',
                         'type': 'string',
                         'enum': ['off', 'heating', 'cooling'],
                         'description': 'The current state',
                         'readOnly': True,
                     }))

        self.mode: Value = Value('off', self.set_mode)
        self.add_property(
            Property(self,
                     'mode',
                     self.mode,
                     metadata={
                         '@type': 'ThermostatModeProperty',
                         'title': 'Mode',
                         'type': 'string',
                         'enum': ['off', 'heat', 'cool', 'auto'],
                         'description': 'The current mode',
                         'readOnly': False,
                     }))

        self.update_period: float = 1000.0
        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_temp,
            self.update_period
        )
        self.timer.start()

    def set_mode(self, mode: str) -> None:
        logging.debug("Setting mode to %s" % mode)
        self.update_state(mode=mode)

    def set_target(self, target: float) -> None:
        logging.debug("Setting target temp to %d" % target)
        self.update_state(target=target)

    def update_temp(self):
        current: float = self.current_temp.get()
        state: str = self.state.get()
        if state == "off":
            return
        elif state == "heating":
            current += round(0.5 * random.random(), 1) + 0.1
        elif state == "cooling":
            current -= round(0.5 * random.random(), 1) + 0.1
        self.current_temp.notify_of_external_update(current)
        self.update_state()

    def update_state(self, mode: str = None, target: float = None):
        if mode is None:
            mode = self.mode.get()
        if target is None:
            target = self.target_temp.get()
        current: float = self.current_temp.get()
        if current > target and mode in ["auto", "cool"]:
            # Set state to cooling
            logging.debug("Setting state to cooling")
            self.state.notify_of_external_update('cooling')
        elif current < target and mode in ["auto", "heat"]:
            # Set state to heating
            logging.debug("Setting state to heating")
            self.state.notify_of_external_update('heating')
        else:
            # Set state to off
            logging.debug("Setting state to off")
            self.state.notify_of_external_update('off')

    def cancel_update(self):
        self.timer.stop()


def run_server():
    thing = SIISHVAC()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(SingleThing(thing), port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        thing.cancel_update()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
