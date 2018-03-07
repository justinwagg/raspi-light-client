import time
from mqtt_class import MyMQTTClass, historical_settings, getLastSettings
import datetime

if bool(historical_settings) == False:
    getLastSettings()

mqttc = MyMQTTClass()
rc = mqttc.run()


try:
    while True:
        time.sleep(1)
        # print(historical_settings[-1])

        if historical_settings[-1].on_time <= datetime.datetime.now().time() <= historical_settings[-1].off_time:
            print('On')
        else:
            print('OFF')

 
except:
    print( "exiting")
    mqttc.disconnect()
    mqttc.loop_stop()