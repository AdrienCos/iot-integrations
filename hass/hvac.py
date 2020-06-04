# from config_node import *
import paho.mqtt.client as mqtt
import threading
import config as cfg

from siisthing import SIISThing

from hardware.thermometer import Thermometer
from hardware.relay import Relay


class SIISHVAC(SIISThing):
    def __init__(self, name: str = "mqtt_hvac_1"):
        SIISThing.__init__(self, name)
        self.last_mode: str = ""
        self.last_action: str = "off"
        self.last_target: float = 0
        self.last_temp: float = 20
        self.outside_temp: float = 20
        self.thermal_cond: float = 0.05  # 1/min
        self.heating_efficiency: float = 0.5  # C/min
        self.cooling_efficiency: float = 0.5  # C/min

        self.temp_state_topic: str = cfg.base_topic + self.name + "/temperature" + cfg.state_suffix
        self.action_state_topic: str = cfg.base_topic + self.name + "/action" + cfg.state_suffix
        self.mode_set_topic: str = cfg.base_topic + self.name + "/mode" + cfg.set_suffix
        self.mode_state_topic: str = cfg.base_topic + self.name + "/mode" + cfg.state_suffix
        self.target_temperature_set: str = cfg.base_topic + self.name + "/target_temperature" + cfg.set_suffix
        self.target_temperature_state: str = cfg.base_topic + self.name + "/target_temperature" + cfg.state_suffix

        self.thermometer: Thermometer = Thermometer()
        self.heater_cooler: Relay = Relay(cfg.pin)

    def calculate_temp(self) -> float:
        "Uses the outside temp, last temp, and the state of the HVAC to calculate the new inside temp"
        if self.last_action == "heating":
            hvac_effect = cfg.update_delay * self.heating_efficiency
        elif self.last_action == "cooling":
            hvac_effect = cfg.update_delay * self.cooling_efficiency
        else:
            hvac_effect = 0
        temp_leakage = cfg.update_delay * self.thermal_cond * (self.outside_temp - self.last_temp)
        new_temp = self.last_temp + temp_leakage + hvac_effect
        _ = self.thermometer.value
        return new_temp

    def start_polling(self) -> None:
        temp: float = self.calculate_temp()
        self.last_temp = temp
        self.client.publish(self.temp_state_topic, payload=("%0.1f" % (self.last_temp)), qos=1, retain=True)
        if self.last_mode == "cool" and self.last_target < temp:
            payload = "cooling"
        elif self.last_mode == "heat" and self.last_target > temp:
            payload = "heating"
        elif self.last_mode == "fan_only":
            payload = "fan"
        elif self.last_mode == "off":
            payload = "off"
        else:
            payload = "idle"
        if self.auto_update:
            self.set_action(payload)
            self.client.publish(self.action_state_topic, payload=self.last_action, qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def set_action(self, action: str) -> None:
        if action == "off":
            self.heater_cooler.unset()
        else:
            self.heater_cooler.set()
        self.last_action = action

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        self.client.subscribe(self.mode_set_topic)
        self.client.subscribe(self.target_temperature_set)
        self.client.subscribe(self.scheduler_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the light in a specific config
        if message.topic == self.target_temperature_set:
            # Read the target temp
            target_temp: float = float(message.payload)
            print("Setting the target temp at %0.1f" % target_temp)
            self.last_target = target_temp
            # Echo it back
            response = str(target_temp)
            self.client.publish(self.target_temperature_state, response, qos=1, retain=True)
        elif message.topic == self.mode_set_topic:
            # Read the fan setting
            mode_setting: str = message.payload.decode("utf-8")
            print("Setting mode to %s" % mode_setting)
            self.last_mode = mode_setting
            # Echo it back
            response = mode_setting
            self.client.publish(self.mode_state_topic, response, qos=1, retain=True)
        elif message.topic == self.scheduler_topic:
            # Detemine if it is a temp or mode update
            payload = message.payload.decode("utf-8")
            try:
                # Read the new outside temp
                temp: float = float(payload)
                print(f"Setting outside temp to {temp}C")
                self.outside_temp = temp
            except ValueError:
                # Set the new mode, disable auto_update
                self.auto_update = False
                state: str = payload
                if state == "OFF":
                    self.set_action("off")
                elif state == "HEAT":
                    self.set_action("heating")
                elif state == "COOL":
                    self.set_action("cooling")

        else:
            # This should not happen, we are not subscribed to anything else
            print("Unexpected message received, channel: %s" % message.topic)
        pass

    def start(self):
        self.connect()
        self.client.loop_start()
        self.start_polling()


# Start polling the files
if __name__ == "__main__":
    hvac = SIISHVAC()
    hvac.start()
