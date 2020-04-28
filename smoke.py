# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading

# Global variables
# client: mqtt.Client = None
broker_addr: str = "hass.local"
client_name: str = "mqtt_smoke_1"
base_topic: str = "home/"
state_topic: str = base_topic + client_name + "/state"
available_topic: str = base_topic + client_name + "/available"
update_delay: float = 1


def get_state() -> str:
    # Replace code here with actual device querying
    return "ON" if random.random() > 0.7 else "OFF"


def start_polling(client: mqtt.Client) -> None:
    client.publish(state_topic, payload=get_state(), qos=1, retain=True)
    threading.Timer(update_delay, start_polling, [client]).start()


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))
    client.publish(available_topic, payload="online", qos=1, retain=True)
    client.publish(state_topic, payload=get_state(), qos=1, retain=True)


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
