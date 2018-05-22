import paho.mqtt.client as mqtt
from settings import Settings, historical_settings
import json
import sqlite3
from printer import a_print
from config import Config

class MyMQTTClass(mqtt.Client):

    def on_connect(self, mqttc, obj, flags, rc):
        # print("rc: "+str(rc))
        a_print("rc: "+str(rc), 'mqtt')

    def on_message(self, mqttc, obj, msg):
        # print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        # print('Appending to historical_settings')
        a_print('Recieved new settings', 'mqtt')
        a_print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload), 'mqtt')
        received_data = json.loads(msg.payload)
        historical_settings.append(Settings(received_data, insert=True))
        a_print('Appended to historical_settings', 'mqtt')

    def on_publish(self, mqttc, obj, mid):
        # print("mid: "+str(mid))
        a_print("mid: "+str(mid), 'mqtt')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        # print("Subscribed: "+str(mid)+" "+str(granted_qos))
        a_print("Subscribed: "+str(mid)+" "+str(granted_qos), 'mqtt')

    def on_log(self, mqttc, obj, level, string):
        # print(string)
        a_print(string, 'mqtt')

    def run(self):
        self.connect(Config.broker)
        self.subscribe(Config.topic, 1)
        self.loop_start()
