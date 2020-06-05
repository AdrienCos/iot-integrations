from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import config as cfg
from typing import Tuple

import paho.mqtt.client as mqtt

from siisthing import SIISThing

from hardware.light import RGBLight


class SIISLight(SIISThing):
    """A dimmable light that logs received commands to stdout."""

    def __init__(self):
        SIISThing.__init__(
            self,
            "mqtt_light_1",
            'urn:dev:siis:light',
            'My Lamp',
            ['OnOffSwitch', 'Light'],
            'A web connected lamp'
        )

        self.on_state: Value = Value(False, self.set_state)
        self.add_property(
            Property(self,
                     'on',
                     self.on_state,
                     metadata={
                         '@type': 'OnOffProperty',
                         'title': 'On/Off',
                         'type': 'boolean',
                         'description': 'Whether the lamp is turned on',
                     }))

        self.brightness_state: Value = Value(100, self.set_brightness)
        self.add_property(
            Property(self,
                     'brightness',
                     self.brightness_state,
                     metadata={
                         '@type': 'BrightnessProperty',
                         'title': 'Brightness',
                         'type': 'integer',
                         'description': 'The level of light from 0-100',
                         'minimum': 0,
                         'maximum': 100,
                         'unit': 'percent',
                     }))

        self.color_state: Value = Value("#FFFFFF", self.set_color)
        self.add_property(
            Property(self,
                     'color',
                     self.color_state,
                     metadata={
                         '@type': 'ColorProperty',
                         'title': 'Color',
                         'type': 'string',
                         'description': 'The color of the light in hex RGB',
                     }))

        self.temperature_state: Value = Value(2700, self.set_temperature)
        self.add_property(
            Property(self,
                     'temperature',
                     self.temperature_state,
                     metadata={
                         '@type': 'ColorTemperatureProperty',
                         'title': 'Temperature',
                         'type': 'integer',
                         'description': 'The temperature of the light in Kelvin',
                         'minimum': 2200,
                         'maximum': 6500,
                         'unit': 'kelvin',
                     }))

        self.color_mode_state: Value = Value("temperature", lambda v: logging.debug("Color mode is now %s" % v))
        self.add_property(
            Property(self,
                     'colorMode',
                     self.color_mode_state,
                     metadata={
                         '@type': 'ColorModeProperty',
                         'title': 'Color Mode',
                         'type': 'string',
                         'description': 'The color mode of the light',
                         'enum': ['color', 'temperature'],
                         'readOnly': True
                     }))

        self.device = RGBLight(cfg.pin)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            payload: str = message.payload.decode()
            if payload == "ON":
                self.on_state.notify_of_external_update(True)
            elif payload == "OFF":
                self.on_state.notify_of_external_update(False)
            elif payload == "BRI":
                self.brightness_state.notify_of_external_update(100)
            elif payload == "TEMP":
                self.temperature_state.notify_of_external_update(3400)
            elif payload == "COL":
                self.color_state.notify_of_external_update("#130296")
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def set_state(self, v: bool):
        logging.debug("On-state is now %d" % v)
        if v:
            self.device.on()
        else:
            self.device.off()

    def set_brightness(self, v):
        logging.debug("Brightness is now %d" % v)
        self.device.brightness = v

    def set_temperature(self, v):
        logging.debug("Temperature is now %d" % v)
        self.color_mode_state.notify_of_external_update('temperature')
        self.device.temperature = v

    def set_color(self, v):
        logging.debug("Color is now %s" % v)
        self.color_mode_state.notify_of_external_update('color')
        self.device.color = self.hex_to_tuple(v)

    @staticmethod
    def hex_to_tuple(self, hex) -> Tuple[int, ...]:
        hex_noo_hash = hex[1:]
        color: Tuple[int, ...] = tuple(i for i in bytes.fromhex(hex_noo_hash))
        return color


def run_server():
    thing = SIISLight()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(SingleThing(thing), port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
