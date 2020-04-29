from lock import SIISLock
from light import SIISLight
from hvac import SIISHVAC
from sensor import SIISSensor
from smoke import SIISSmoke
from switch import SIISSwitch
from tv import SIISTV

import threading

lock = SIISLock()
hvac = SIISHVAC()
light = SIISLight()
sensor = SIISSensor()
smoke = SIISSmoke()
switch = SIISSwitch()
tv = SIISTV()

devices = [
    lock,
    hvac,
    light,
    sensor,
    smoke,
    switch,
    tv
]

for device in devices:
    print(device)
    threading.Thread(target=device.start).start()
