from __future__ import division
from webthing import (Property, SingleThing, Value,
                      WebThingServer)
import logging
import tornado.ioloop
import config as cfg

from hardware.switch import Switch
from siisthing import SIISThing
import paho.mqtt.client as mqtt


class SIISSwitch(SIISThing):
    """A binary sensor."""

    def __init__(self):
        SIISThing.__init__(
            self,
            "switch_1",
            'urn:dev:siis:switch',
            'My Switch',
            ['BinarySensor'],
            'A web connected lamp'
        )
        self.update_period: float = cfg.update_delay * 1000
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

        self.device = Switch(cfg.pin)

        self.timer: tornado.ioloop.PeriodicCallback = tornado.ioloop.PeriodicCallback(
            self.update_state,
            self.update_period
        )
        self.timer.start()

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            # Stop the timer to prevent automatic changes
            self.auto_update = False
            payload: str = message.payload.decode()
            if payload == "ON":
                self.state.notify_of_external_update(True)
            elif payload == "OFF":
                self.state.notify_of_external_update(False)
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def update_state(self) -> None:
        new_state: bool = self.device.value
        logging.debug("Switch state is now %d" % new_state)
        logging.debug(self.client.is_connected())
        if self.auto_update:
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
