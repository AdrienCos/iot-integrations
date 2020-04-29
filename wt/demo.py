from hvac import SIISHVAC
from light import SIISLight
from lock import SIISLock
from sensor import SIISThermometer, SIISBarometer, SIISHygrometer
from smoke import SIISSmokeDetector
from switch import SIISSwitch
from tv import SIISTV

import logging
from webthing import WebThingServer, MultipleThings


def run_server():
    # Create a thing that represents a dimmable light
    thermometer = SIISThermometer()
    barometer = SIISBarometer()
    hygrometer = SIISHygrometer()
    hvac = SIISHVAC()
    light = SIISLight()
    lock = SIISLock()
    tv = SIISTV()
    switch = SIISSwitch()
    smoke = SIISSmokeDetector()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(
        MultipleThings(
            [
                thermometer,
                barometer,
                hygrometer,
                hvac,
                light,
                lock,
                tv,
                switch,
                smoke
            ],
            'WeatherStation'),
        port=8888
    )
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
