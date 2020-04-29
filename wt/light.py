from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging


class SIISLight(Thing):
    """A dimmable light that logs received commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:light',
            'My Multi Lamp',
            ['OnOffSwitch', 'Light'],
            'A web connected lamp'
        )

        self.add_property(
            Property(self,
                     'on',
                     Value(True, lambda v: logging.debug('On-State is now %s' % v)),
                     metadata={
                         '@type': 'OnOffProperty',
                         'title': 'On/Off',
                         'type': 'boolean',
                         'description': 'Whether the lamp is turned on',
                     }))

        self.add_property(
            Property(self,
                     'brightness',
                     Value(100, self.set_brightness),
                     metadata={
                         '@type': 'BrightnessProperty',
                         'title': 'Brightness',
                         'type': 'integer',
                         'description': 'The level of light from 0-100',
                         'minimum': 0,
                         'maximum': 100,
                         'unit': 'percent',
                     }))

        self.add_property(
            Property(self,
                     'color',
                     Value("#FFFFFF", self.set_color),
                     metadata={
                         '@type': 'ColorProperty',
                         'title': 'Color',
                         'type': 'string',
                         'description': 'The color of the light in hex RGB',
                     }))
        self.add_property(
            Property(self,
                     'temperature',
                     Value(2700, self.set_temperature),
                     metadata={
                         '@type': 'ColorTemperatureProperty',
                         'title': 'Temperature',
                         'type': 'integer',
                         'description': 'The temperature of the light in Kelvin',
                         'minimum': 2200,
                         'maximum': 6500,
                         'unit': 'kelvin',
                     }))

        self.add_property(
            Property(self,
                     'colorMode',
                     Value("temperature", lambda v: logging.debug("Color mode is now %s" % v)),
                     metadata={
                         '@type': 'ColorModeProperty',
                         'title': 'Color Mode',
                         'type': 'string',
                         'description': 'The color mode of the light',
                         'enum': ['color', 'temperature'],
                         'readOnly': True
                     }))

    def set_brightness(self, v):
        logging.debug("Brightness is now %d" % v)

    def set_temperature(self, v):
        logging.debug("Temperature is now %d" % v)
        self.properties['colorMode'].value.notify_of_external_update('temperature')

    def set_color(self, v):
        logging.debug("Color is now %s" % v)
        self.properties['colorMode'].value.notify_of_external_update('color')


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
