import paho.mqtt.client as mqtt
from settings import Settings
import json
import sqlite3

historical_settings = []

class MyMQTTClass(mqtt.Client):

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        received_data = json.loads(msg.payload)
        print('Appending to historical_settings')
        historical_settings.append(Settings(received_data, insert=True))

    def on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self.connect("192.168.1.55")
        self.subscribe("lights.bathroom", 1)
        self.loop_start()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def getLastSettings():
    print('No settings, getting defaults from SQLite')
    conn = sqlite3.connect('settings.db', check_same_thread=False)
    c = conn.cursor()
    c.row_factory = dict_factory
    c.execute('select high, low, manual, off_time, on_time, received_on from settings a inner join (select max(id) as id from settings) b on a.id=b.id')
    results = c.fetchall()
    conn.close()
    historical_settings.append(Settings(results[0]))