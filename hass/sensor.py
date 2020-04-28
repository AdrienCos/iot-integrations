# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading

# Global variables
# client: mqtt.Client = None
broker_addr: str = "hass.local"
client_name: str = "mqtt_sensor_1"
base_topic: str = "home/"
available_topic: str = base_topic + client_name + "/available"
temp_state_topic = base_topic + client_name + "/thermometer" + "/state"
humidity_state_topic = base_topic + client_name + "/hygrometer" + "/state"
pressure_state_topic = base_topic + client_name + "/barometer" + "/state"
update_delay: float = 1


def get_temp() -> str:
    # Replace code here with actual device querying
    return "%0.1f" % (random.random() * 20 + 10)


def get_humidity() -> str:
    # Replace code here with actual device querying
    return "%0.1f" % (random.random() * 100)


def get_pressure() -> str:
    # Replace code here with actual device querying
    return "%0.1f" % (random.random() * 6 + 1015.25)


def start_polling(client: mqtt.Client) -> None:
    client.publish(temp_state_topic, payload=get_temp(), qos=1, retain=True)
    client.publish(humidity_state_topic, payload=get_humidity(), qos=1, retain=True)
    client.publish(pressure_state_topic, payload=get_pressure(), qos=1, retain=True)
    threading.Timer(update_delay, start_polling, [client]).start()


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))
    client.publish(available_topic, payload="online", qos=1, retain=True)
    client.publish(temp_state_topic, payload=get_temp(), qos=1, retain=True)
    client.publish(humidity_state_topic, payload=get_humidity(), qos=1, retain=True)
    client.publish(pressure_state_topic, payload=get_pressure(), qos=1, retain=True)


def connect(addr: str = broker_addr) -> mqtt.Client:
    client = mqtt.Client(client_name)
    client.on_connect = on_connect
    client.username_pw_set("adrien", "mqttpassword")
    client.will_set(available_topic, payload="offline", qos=1, retain=True)
    client.connect(broker_addr, port=1883)
    return client


# Start polling the files
if __name__ == "__main__":
    client: mqtt.Client = connect(broker_addr)
    client.loop_start()
    start_polling(client)
