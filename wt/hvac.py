from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import tornado.ioloop
import random

import config as cfg
import paho.mqtt.client as mqtt


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

        self.outside_temp: float = 20
        self.heating_efficiency: float = 0.5
        self.cooling_efficiency: float = 0.5
        self.thermal_cond: float = 0.05
        self.name = "mqtt_hvac_1"
        self.scheduler_topic = cfg.scheduler_topic + self.name
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(cfg.username, cfg.password)
        self.connect()

        self.update_period: float = cfg.update_delay * 1000.0
        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_temp,
            self.update_period
        )
        self.timer.start()

    def connect(self):
        self.client.connect(cfg.broker_addr, port=cfg.port)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        logging.debug("Connected to broker")
        self.client.subscribe(self.scheduler_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            new_outside_temp = float(message.payload.decode("utf-8"))
            logging.debug(f"Setting outside temperature to {new_outside_temp}C")
            self.outside_temp = new_outside_temp
        else:
            logging.error(f"Message received from invalid topic: {message.topic}")

    def set_mode(self, mode: str) -> None:
        logging.debug("Setting mode to %s" % mode)
        self.update_state(mode=mode)

    def set_target(self, target: float) -> None:
        logging.debug("Setting target temp to %d" % target)
        self.update_state(target=target)

    def update_temp(self):
        "Uses the outside temp, last temp, and the state of the HVAC to calculate the new inside temp"
        current: float = self.current_temp.get()
        state: str = self.state.get()
        outside: float = self.outside_temp
        if state == "heating":
            hvac_effect = self.update_period * self.heating_efficiency
        elif state == "cooling":
            hvac_effect = self.update_period * self.cooling_efficiency
        else:
            hvac_effect = 0
        temp_leakage = self.update_period * self.thermal_cond * (outside - current)
        new_temp = current + temp_leakage + hvac_effect
        self.current_temp.notify_of_external_update(new_temp)
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
