from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging


class SIISTV(Thing):
    """A TV that logs received commands to stdout."""

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:siis:tv',
            'My TV',
            ['OnOffSwitch'],
            'A web connected TV'
        )

        self.state: Value = Value(False, self.set_state)
        self.add_property(
            Property(self,
                     'on',
                     self.state,
                     metadata={
                         '@type': 'OnOffProperty',
                         'title': 'On state',
                         'type': 'boolean',
                         'description': 'Whether the TV is on',
                         'readOnly': False,
                     }))

    def set_state(self, state: bool) -> None:
        logging.debug(f"TV is now {'ON' if state else 'OFF'}")
        # Handle the hardware side


def run_server():
    thing = SIISTV()

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
