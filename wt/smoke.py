from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer, Event)
import logging
import tornado.ioloop
import random
import config as cfg

from hardware.smoke import SmokeDetector


class AlarmEvent(Event):
    def __init__(self, thing, data=None):
        Event.__init__(self, thing, name='alarm', data=data)
        logging.debug("Alarm event")


class SIISSmokeDetector(Thing):
    """A smoke detector that logs detected events commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:smoke',
            'My Smoke Detector',
            ['Alarm'],
            'A web connected smoke detector'
        )
        self.state: Value = Value(False)
        self.update_period: float = 1000.0
        self.add_property(
            Property(self,
                     'on',
                     self.state,
                     metadata={
                         '@type': 'AlarmProperty',
                         'title': 'Smoke detected',
                         'type': 'boolean',
                         'description': 'Whether smoke has been detected',
                         'readOnly': True,
                     }))
        self.add_available_event(
            'alarm',
            {'description': 'Smoke detected'}
        )

        self.device = SmokeDetector(cfg.pin, self.activated, self.deactivated)
        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def activated(self) -> None:
        pass

    def deactivated(self) -> None:
        pass

    def update_state(self) -> None:
        new_state: bool = self.device.state
        logging.debug("State is now %d" % new_state)
        self.state.notify_of_external_update(new_state)
        if new_state:
            self.add_event(AlarmEvent(self))


def run_server():
    thing = SIISSmokeDetector()

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
