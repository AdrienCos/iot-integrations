from __future__ import division
from webthing import (Action, Event, Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import time
import uuid


class OverheatedEvent(Event):

    def __init__(self, thing, data):
        logging.debug("Overheated event")
        Event.__init__(self, thing, 'overheated', data=data)


class FadeAction(Action):

    def __init__(self, thing, input_):
        logging.debug("Fade action")
        Action.__init__(self, uuid.uuid4().hex, thing, 'fade', input_=input_)

    def perform_action(self):
        self.thing.set_property('brightness', self.input['brightness'])
        time.sleep(self.input['duration'] / 1000)
        self.thing.add_event(OverheatedEvent(self.thing, 102))
        self.thing.set_property('on', False)


def make_thing():
    thing = Thing(
        'urn:dev:ops:my-lamp-1234',
        'My Simple Lamp',
        ['OnOffSwitch', 'Light'],
        'A web connected lamp'
    )

    thing.add_property(
        Property(thing,
                 'on',
                 Value(True, lambda v: logging.debug("On-state is now %s" % v)),
                 metadata={
                     '@type': 'OnOffProperty',
                     'title': 'On/Off',
                     'type': 'boolean',
                     'description': 'Whether the lamp is turned on',
                 }))
    thing.add_property(
        Property(thing,
                 'brightness',
                 Value(50, lambda v: logging.debug("Brightness is now %d" % v)),
                 metadata={
                     '@type': 'BrightnessProperty',
                     'title': 'Brightness',
                     'type': 'integer',
                     'description': 'The level of light from 0-100',
                     'minimum': 0,
                     'maximum': 100,
                     'unit': 'percent',
                 }))

    thing.add_property(
        Property(thing,
                 "URL",
                 Value(None),
                 metadata={
                     '@type': 'ImageProperty',
                     'title': 'Image URL',
                     'type': 'null',
                     'description': 'URL of the image to be played',
                     'links': [{
                         'rel': 'alternate',
                         'href': '/static/current.jpg',
                         'mediaType': 'image/jpeg',
                     }, ],

                 }))

    thing.add_available_action(
        'fade',
        {
            'title': 'Fade',
            'description': 'Fade the lamp to a given level',
            'input': {
                'type': 'object',
                'required': [
                    'brightness',
                    'duration',
                ],
                'properties': {
                    'brightness': {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 100,
                        'unit': 'percent',
                    },
                    'duration': {
                        'type': 'integer',
                        'minimum': 1,
                        'unit': 'milliseconds',
                    },
                },
            },
        },
        FadeAction)

    thing.add_available_event(
        'overheated',
        {
            'description':
            'The lamp has exceeded its safe operating temperature',
            'type': 'number',
            'unit': 'degree celsius',
        })

    return thing


def run_server():
    thing = make_thing()

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
