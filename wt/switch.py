from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import tornado.ioloop
import random


class SIISSwitch(Thing):
    """A dimmable light that logs received commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:switch',
            'My Switch',
            ['BinarySensor'],
            'A web connected lamp'
        )
        self.update_period: float = 10000.0
        self.state: Value = Value(False)
        self.add_property(
            Property(self,
                     'state',
                     self.state,
                     metadata={
                         '@type': 'BooleanProperty',
                         'title': 'On/Off',
                         'type': 'boolean',
                         'description': 'Whether the switch is turned on',
                         'readOnly': True,
                     }))

        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def update_state(self) -> None:
        new_state: bool = True if random.random() > 0.5 else False
        logging.debug("Switch state is now %d" % new_state)
        self.state.notify_of_external_update(new_state)

    def cancel_update(self):
        self.timer.stop()


def run_server():
    thing = SIISSwitch()

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
