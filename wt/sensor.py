from __future__ import division, print_function
from webthing import (MultipleThings, Property, Thing, Value,
                      WebThingServer)
import logging
import random
import tornado.ioloop
import config as cfg

from hardware.thermometer import Thermometer
from hardware.barometer import Barometer


class SIISThermometer(Thing):
    """A thermometer that logs detected events commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:thermometer',
            'My Thermometer',
            ['TemperatureSensor'],
            'A web connected thermometer'
        )
        self.temp: Value = Value(20.0)
        self.update_period: float = cfg.pin * 1000
        self.add_property(
            Property(self,
                     'temperature',
                     self.temp,
                     metadata={
                         '@type': 'TemperatureProperty',
                         'title': 'Temperature',
                         'type': 'number',
                         'description': 'Current temperature',
                         'readOnly': True,
                         'multipleOf': 0.1,
                     }))

        self.device = Thermometer()

        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def update_state(self) -> None:
        new_temp: float = self.device.value
        logging.debug("Temperature is now %0.1fC" % new_temp)
        self.temp.notify_of_external_update(new_temp)


class SIISBarometer(Thing):
    """A barometer that logs detected events commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:barometer',
            'My Barometer',
            ['MultiLevelSensor'],
            'A web connected barometer'
        )
        self.pressure: Value = Value(1018.2)
        self.update_period: float = cfg.pin * 1000
        self.add_property(
            Property(self,
                     'temperature',
                     self.pressure,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Pressure',
                         'type': 'number',
                         'minimum': 900,
                         'maximum': 1100,
                         'unit': 'hPa',
                         'description': 'Current atomspheric pressure',
                         'readOnly': True,
                         'multipleOf': 0.1,
                     }))

        self.device = Barometer()

        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def update_state(self) -> None:
        new_pressure: float = self.device.value
        logging.debug("Pressure is now %0.1fhPa" % new_pressure)
        self.pressure.notify_of_external_update(new_pressure)


class SIISHygrometer(Thing):
    """A hygrometer that logs detected events commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:hygrometer',
            'My Hygrometer',
            ['MultiLevelSensor'],
            'A web connected hygrometer'
        )
        self.humidity: Value = Value(50)
        self.update_period: float = 1000.0
        self.add_property(
            Property(self,
                     'humidity',
                     self.humidity,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Humidity',
                         'type': 'number',
                         'unit': 'percent',
                         'description': 'Current air humdity',
                         'readOnly': True,
                         'multipleOf': 0.1,
                     }))

        self.device = Barometer()

        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def update_state(self) -> None:
        _ = self.device.value
        new_humidity: float = self.humidity.last_value
        new_humidity += random.random() * 2 - 1
        logging.debug("Pressure is now %0.1f" % new_humidity)
        self.humidity.notify_of_external_update(new_humidity)


def run_server():
    # Create a thing that represents a dimmable light
    thermometer = SIISThermometer()
    barometer = SIISBarometer()
    hygrometer = SIISHygrometer()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(MultipleThings([thermometer, barometer, hygrometer],
                                           'WeatherStation'),
                            port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        thermometer.cancel_update_level_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
