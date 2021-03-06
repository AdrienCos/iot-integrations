from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import paho.mqtt.client as mqtt

from siisthing import SIISThing

from hardware.tv import TV


class SIISTV(SIISThing):
    """A TV that logs received commands to stdout."""

    def __init__(self):
        SIISThing.__init__(
            self,
            "tv_1",
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

        self.device = TV()

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            new_state = message.payload.decode("utf-8")
            logging.debug(f"Setting state to {new_state}")
            if new_state == "ON":
                self.state.notify_of_external_update(True)
                self.device.on()
            elif new_state == "OFF":
                self.state.notify_of_external_update(False)
                self.device.off()
            else:
                logging.error(f"Invalid state received: {new_state}")
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

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
