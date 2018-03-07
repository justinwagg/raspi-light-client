import pigpio
import time
import datetime
import re
from mqtt_class import MyMQTTClass, historical_settings, getLastSettings
import sys

class Settings(object):
    def __init__(self):
        self.low = 30
        self.high = 100
        self.manual = 255
        self.on_time = datetime.datetime.strptime('12:00:00', '%H:%M:%S').time()
        self.off_time = datetime.datetime.strptime('23:00:00', '%H:%M:%S').time()      


class Lights(object):

    def __init__(self):
        self.led_array = 27
        self.switch = 4 
        self.pir = 17
        self.pi = pigpio.pi()

        self.pi.set_mode(self.switch, pigpio.INPUT)
        # self.pi.set_pull_up_down(self.switch, pigpio.PUD_DOWN)
        # self.pi.set_glitch_filter(self.switch, 5000)
        # self.pi.set_noise_filter(self.switch, 300000, 100)
        

        self.pi.set_mode(self.pir, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pir, pigpio.PUD_DOWN)
        # self.pi.set_glitch_filter(self.pir, 5000)
        # self.pi.set_noise_filter(self.pir, 300000, 100)

        self.pi.set_mode(self.led_array, pigpio.OUTPUT)

        self.buttonState = False
        self.buttonMaxOnTime = (1000*60*20)

        self.pirState = False
        self.allowPIR = True

        self.pirMaxOnTime = (1000*60*2)
        
        self.currentLight = None
        self.lastHit = int(round(time.time() * 1000)) - 1000
        self.pirHit = self.lastHit

        # Settings
        self.low = None 
        self.high = None
        self.manual = None        
        self.on_time = None
        self.off_time = None

        self.target = self.low

        self.a_print('Initialized', 'alert')

    def event_cbf(self, gpio, level, tick):
    # def event_cbf(self, gpio):    
        # print(gpio, level, tick)
        thisHit = int(round(time.time() * 1000))
        time_delta = thisHit - self.lastHit
        if gpio == self.switch:
            if(time_delta >= 1000):
            # if gpio == self.switch:
                self.a_print('Button Pressed: It\'s been {} seconds since the last input. Flipping self.buttonState.'.format(time_delta/1000), 'input')
                self.flip_button()
                if self.buttonState == True:

                    self.target = self.manual
                    self.a_print('The target light is now set to {}'.format(self.target), 'target')

                    self.pir_allow(False)

                elif self.buttonState == False:

                    if self.pirState == True:
                        self.target = self.high
                        self.a_print('The target light is now set to {}, following pirState'.format(self.target), 'target')
                    else:
                        self.target = self.low
                        self.a_print('The target light is now set to {}'.format(self.target), 'target')
                       
                    self.pir_allow(True)                
                self.lastHit = thisHit

        elif gpio == self.pir:

            if self.allowPIR == True:

                if self.pirState == False:
                    self.a_print('PIR Triggered: It\'s been {} seconds since the last trigger. Flipping self.pirState'.format(time_delta/1000), 'input')                    
                    self.a_print('The PIR state is {}'.format(self.pirState), 'alert')
                 
                    self.pirState = True
                    self.a_print('The PIR state is now  {}'.format(self.pirState), 'alert')

                    self.target = self.high
                    self.a_print('The target light is now set to {}'.format(self.target), 'target')

                    self.pirHit = thisHit

                else:
                    self.a_print('PIR Triggered: PIR state is already {}'.format(self.pirState) ,'input')
                    self.pirHit = thisHit


            else:
                self.a_print('PIR triggered, but buttonState is True, resetting PIR hit time', 'input')

                self.pirHit = thisHit
                self.a_print('pirHit = {}'.format(self.pirHit), 'alert')
                self.pirState = True


    def pir_allow(self, state):
        self.a_print('PIR eligibility is: {}'.format(self.allowPIR), 'setting')
        self.allowPIR = state
        self.a_print('PIR eligibility is now: {}'.format(self.allowPIR), 'setting')      

    def flip_button(self):
        self.a_print('The button state is: {}'.format(self.buttonState), 'setting')
        self.buttonState = not self.buttonState
        self.a_print('The button state is now: {}'.format(self.buttonState), 'setting')

    def input_update(self):
        now = int(round(time.time() * 1000))
        if self.buttonState:
            if((now - self.lastHit) >= self.buttonMaxOnTime):
                self.a_print('Button was turned on {} seconds ago, turning light down.'.format(self.buttonMaxOnTime/1000), 'auto_off')

                self.flip_button()

                if self.pirState == True:
                    self.target = self.high
                    self.a_print('The target light is now set to {}, following pirState'.format(self.target), 'target')
                else:
                    self.target = self.low
                    self.a_print('The target light is now set to {}'.format(self.target), 'target')

        if self.pirState and self.allowPIR:
            delta = now - self.pirHit
            if(delta >= self.pirMaxOnTime):

                self.a_print('PIR was turned on over {} seconds ago, turning light down.'.format(self.pirMaxOnTime/1000), 'auto_off')
                self.a_print('The PIR state is {}'.format(self.pirState), 'setting')
                self.pirState = not self.pirState
                self.a_print('The PIR state is now {}'.format(self.pirState), 'setting')
                self.target = self.low
                self.a_print('The target light is now set to {}'.format(self.target), 'target')

    def fade(self, target, pin):
        try:
            current = self.pi.get_PWM_dutycycle(pin)
            self.a_print('Light setting entering fade is {}'.format(current), 'alert')
        except:
            current = 0
            self.a_print('Caught Exception, set current light to {}'.format(current), 'alert')

        if target > current:
            # Fade up
            for i in range(current, target +1):
                # print('fading up, i = {}'.format(i))
                self.pi.set_PWM_dutycycle(pin, i)
                time.sleep(.005)
        elif target < current:
            # Fade down
            for i in range(current, target -1, -1):
                # print('fading down, i = {}'.format(i))
                self.pi.set_PWM_dutycycle(pin, i)
                time.sleep(.005)

        self.a_print('Light setting exiting fade is {}'.format(target), 'alert')


    def set_light(self):
        try:
            self.currentLight = self.pi.get_PWM_dutycycle(self.led_array)
        except:
            self.currentlLight = 0

        if self.currentLight != self.target:
            self.fade(self.target, self.led_array)
        else:
            pass

    def update_settings(self, settings_object, boot=False):
        now = datetime.datetime.now().time()

        self.on_time = settings_object.on_time
        self.off_time = settings_object.off_time 

        self.a_print('self.on_time: {} | self.off_time: {} | now: {}'.format(self.on_time, self.off_time, now), 'alert')
        # print('self.off_time = {}'.format(self.off_time), 'alert')
        # print('now = {}'.format(now), 'alert')

        if now >= self.on_time and now <= self.off_time:
        # if self.on_time >= now <= self.off_time:
            # self.a_print(str(settings_object) + ' True ' + '{:%I:%M %p}'.format(now), 'alert')
            # self.a_print('YES', 'alert')
            self.low = settings_object.low 
            self.high = settings_object.high 
        elif now < self.on_time or now > self.off_time:
        # elif self.on_time <= now >= self.off_time:
            # self.a_print('NO', 'alert')
            # self.a_print(str(settings_object) + ' False ' + '{:%I:%M %p}'.format(now), 'alert')
            self.low = 0 
            self.high = settings_object.low 

        self.manual = settings_object.manual

        if boot:
            self.target = self.low
            self.a_print('Booting - Setting initial target to {}'.format(self.target), 'alert')
        else:
            pass
         
        

    def a_print(self, string, level):
        x = {
            'setting': ' \x1b[30;41mSetting Change\x1b[0m: ',
            'target': ' \x1b[30;42mTarget Change\x1b[0m: ',
            'alert': ' \x1b[31;40mAlert\x1b[0m: ',
            'auto_off': ' \x1b[30;44mAUTO OFF ALERT\x1b[0m: ',
            'input': ' \x1b[30;42mINPUT\x1b[0m: '
        }
        fixed = re.sub('True', '\x1b[32;40mTrue\x1b[0m', string)
        fixed = re.sub('False', '\x1b[31;40mFalse\x1b[0m', fixed)
        print(str(datetime.datetime.now()) + x[level] + fixed)

    def main(self):
        self.update_settings(historical_settings[-1])
        # self.a_print(str(historical_settings[-1]), 'alert')
        self.input_update()
        self.set_light()

print('\n')
print('===============================================================================')
print('BEGIN')
print('===============================================================================\n')

if bool(historical_settings) == False:
    getLastSettings()

lights = Lights()
# settings = Settings()

# lights.update_settings(settings, boot=True)
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
    sys.exit()