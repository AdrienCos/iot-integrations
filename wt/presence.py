from __future__ import division
from webthing import (Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging

import paho.mqtt.client as mqtt
import config as cfg

from siisthing import SIISThing

from hardware.pir import PIR


class SIISPresence(SIISThing):
    """A presence sensor."""

    def __init__(self):
        SIISThing.__init__(
            self,
            "presence_1",
            'urn:dev:siis:presence',
            'My Presence Sensor',
            ['BinarySensor'],
            'A web connected presence sensor'
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

        self.device = PIR(cfg.pin, self.activated, self.deactivated)

        self.name = "mqtt_presence_1"

    def activated(self) -> None:
        pass

    def deactivated(self) -> None:
        pass

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            new_state = message.payload.decode("utf-8")
            _ = self.device.value
            logging.debug(f"Setting state to {new_state}")
            if new_state == "ON":
                self.state.notify_of_external_update(True)
            elif new_state == "OFF":
                self.state.notify_of_external_update(False)
            else:
                logging.error(f"Invalid state received: {new_state}")
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)


def run_server():
    thing = SIISPresence()

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
