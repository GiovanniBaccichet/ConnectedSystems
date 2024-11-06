# Create a prototype of a multi-purpose sensor for a smart home that monitors temperature, humidity, light and motion
# inside a, e.g. living room and sends the data to a local Home Assistant instance.

from machine import Pin,PWM,ADC
from utime import sleep
from dht import DHT22
import ujson

import network
import time

print("Connecting to WiFi", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
while not wlan.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(wlan.ifconfig())
print("WiFi Connected!")

print("Connected Systems - Challenge")

LDR = ADC(28)
pwm = PWM(Pin(15))
dht = DHT22(Pin(15)) 
pir = Pin(5, Pin.IN)

from umqttsimple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "picow-01"
MQTT_BROKER    = "broker.emqx.io"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC_SUB     = "cs-challenge/sub"
MQTT_TOPIC_PUB     = "cs-challenge/pub"
print("Connecting to MQTT server... ", end="")
client = MQTTClient(client_id=MQTT_CLIENT_ID, 
server=MQTT_BROKER, user=MQTT_USER, 
password=MQTT_PASSWORD, 
keepalive=7200,
)

print("")

# The callback function
def sub_callback(topic, msg):
  print("Received: {}:{}".format(topic.decode(), msg.decode()))

client.set_callback(sub_callback)
client.connect()
print("MQTT Connected!")

client.check_msg()

print("")
while True:
    dht.measure()
    temp = dht.temperature()
    hum = dht.humidity()
    lux = LDR.read_u16()
    motion = pir.value()
    print(f"[!] Temperature: {temp}°C  Humidity: {hum}%")
    print(f"[!] Light Value {lux} lux")
    if motion == 1:
       print(f"[!] Motion: {motion}")
    else:
       print(f"[!] Motion: {motion}")
    # print("---------------------------")

    message = ujson.dumps({
        "temp": temp,
        "humidity": hum,
        "lux": lux,
        "motion": motion,
    })

    client.publish(topic=MQTT_TOPIC_PUB, msg=message)

    sleep(1)
