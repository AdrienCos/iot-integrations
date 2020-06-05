from __future__ import division
from webthing import (Action, Property, Thing, SingleThing, Value,
                      WebThingServer)
import logging
import uuid
import paho.mqtt.client as mqtt

import config as cfg
from siisthing import SIISThing

from hardware.servo import ServoMotor


class GenericLockAction(Action):
    def __init__(self, action_type: str, thing, input_):
        self.thing: Thing
        self.action_type: str = action_type
        Action.__init__(self, uuid.uuid4().hex, thing, action_type, input_)

    def perform_action(self):
        self.thing.properties['locked'].value.notify_of_external_update(self.action_type)
        logging.debug("Set the lock to %s" % self.action_type)


class LockAction(GenericLockAction):
    def __init__(self, thing, input_):
        GenericLockAction.__init__(self, "locked", thing, input_)


class UnlockAction(GenericLockAction):
    def __init__(self, thing, input_):
        GenericLockAction.__init__(self, "unlocked", thing, input_)


class SIISLock(SIISThing):
    """A lock that logs received commands to stdout."""

    def __init__(self):
        SIISThing.__init__(
            self,
            "mqtt_lock_1",
            'urn:dev:siis:lock',
            'My Lock',
            ['Lock'],
            'A web connected lock'
        )

        self.state: Value = Value("unlocked", self.set_state)
        self.add_property(
            Property(self,
                     'locked',
                     self.state,
                     metadata={
                         '@type': 'LockedProperty',
                         'title': 'Lock state',
                         'type': 'string',
                         'description': 'Whether the lock is locked',
                         'readOnly': True,
                         'enum': ['locked, unlocked'],
                     }))

        self.add_available_action(
            "lock",
            {
                "title": "Lock",
                "description": "Set the lock to locked state",
            },
            LockAction
        )

        self.add_available_action(
            "unlock",
            {
                "title": "Unlock",
                "description": "Set the lock to unlocked state",
            },
            UnlockAction
        )

        self.device = ServoMotor(cfg.pin)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            # Stop the timer to prevent automatic changes
            payload: str = message.payload.decode()
            if payload == "ON":
                self.perform_action("lock")
                # self.state.notify_of_external_update("locked")
            elif payload == "OFF":
                self.perform_action("unlock")
                # self.state.notify_of_external_update("unlocked")
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def set_state(self, state: str) -> None:
        if state == "unlocked":
            self.device.off()
        elif state == "locked":
            self.device.on()
        else:
            print("Invalid state")


def run_server():
    thing = SIISLock()

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
