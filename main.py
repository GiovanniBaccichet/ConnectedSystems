# Create a prototype of a multi-purpose sensor for a smart home that monitors temperature, humidity, light and motion
# inside a, e.g. living room and sends the data to a local Home Assistant instance.

################################
#                              #
#       Wi-Fi Connection       #
#                              #
################################

import network
import time

print("Connecting to WiFi", end="")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")

# Wait for Raspberry Pi Pico to connect to the network before proceeding
while not wlan.isconnected():
  time.sleep(0.1)

print("WiFi Connected!")


################################
#                              #
#    MQTT Broker Connection    #
#                              #
################################


from umqttsimple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "picow-01"
MQTT_BROKER    = "broker.emqx.io"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC_SUB     = "cs-challenge/sub"
MQTT_TOPIC_PUB     = "cs-challenge/pub"

print("Connecting to MQTT server... ", end="")
print("")

# Client setup
client = MQTTClient(client_id=MQTT_CLIENT_ID, 
server=MQTT_BROKER, user=MQTT_USER, 
password=MQTT_PASSWORD, 
keepalive=7200,
)

# Callback function: defines actions upon receiving a subscribed topic message
def sub_callback(topic, msg):
  print("Received: {}:{}".format(topic.decode(), msg.decode()))

client.set_callback(sub_callback)
client.connect()

print("MQTT Connected!")

################################
#                              #
#     MQTT Check Messages      #
#                              #
################################

# Subscribing to topic
print("Subscribing to topic", MQTT_TOPIC_SUB)
client.subscribe(MQTT_TOPIC_SUB)

# Retrieving last message from the topic
print("Retrieving last message")
client.check_msg()

################################
#                              #
#  Sensor Data Reading & PUB   #
#                              #
################################

from machine import Pin,PWM,ADC
from utime import sleep
from dht import DHT22
import ujson

# Associate PINs to variables
LDR = ADC(28)
pwm = PWM(Pin(15))
dht = DHT22(Pin(15)) 
pir = Pin(5, Pin.IN)

# While loop to read sensor data AND publish them every 10 seconds
while True:

    # Read sensor data
    dht.measure()
    temp = dht.temperature()
    hum = dht.humidity()
    lux = LDR.read_u16()
    motion = pir.value()

    # Display sensor data
    print(f"[!] Temperature: {temp}°C  Humidity: {hum}%")
    print(f"[!] Light Value {lux} lux")
    print(f"[!] Motion: {motion}")

    # Format the MQTT message to publish
    message = ujson.dumps({
        "temp": temp,
        "humidity": hum,
        "lux": lux,
        "motion": motion,
    })

    # Publish the message on the above defined topic
    client.publish(topic=MQTT_TOPIC_PUB, msg=message)

    sleep(10)
