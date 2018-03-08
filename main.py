from mqtt_ import MyMQTTClass
from settings import historical_settings, getLastSettings
import sys
from lights import Lights, pigpio, time


print('\n')
print('===============================================================================')
print('BEGIN')
print('===============================================================================\n')

# If there's no historical settings, pull the last value sfrom SQLite
if bool(historical_settings) == False:
    getLastSettings()

lights = Lights()

lights.update_settings(historical_settings[-1], boot=True)

mqttc = MyMQTTClass()
rc = mqttc.run()

cb1 = lights.pi.callback(lights.switch, pigpio.RISING_EDGE, lights.event_cbf)   
cb2 = lights.pi.callback(lights.pir, pigpio.RISING_EDGE, lights.event_cbf)  


time.sleep(1)
try:
    while True:

        lights.main()
     

except KeyboardInterrupt:
    lights.pi.set_PWM_dutycycle(lights.led_array, 0)
    lights.pi.stop()
    mqttc.disconnect()
    mqttc.loop_stop()    
    exit()
