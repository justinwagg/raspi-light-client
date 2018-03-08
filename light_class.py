import pigpio
import time
from a_print import a_print
import datetime
from settings import historical_settings, getLastSettings

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

        self.currentMode = None

        a_print('Initialized', 'alert')

    def event_cbf(self, gpio, level, tick):
    # def event_cbf(self, gpio):    
        # print(gpio, level, tick)
        thisHit = int(round(time.time() * 1000))
        time_delta = thisHit - self.lastHit
        if gpio == self.switch:
            if(time_delta >= 1000):
            # if gpio == self.switch:
                a_print('Button Pressed: It\'s been {} seconds since the last input. Flipping self.buttonState.'.format(time_delta/1000), 'input')
                self.flip_button()
                if self.buttonState == True:

                    self.target = self.manual
                    a_print('The target light is now set to {}'.format(self.target), 'target')

                    self.pir_allow(False)

                elif self.buttonState == False:

                    if self.pirState == True:
                        self.target = self.high
                        a_print('The target light is now set to {}, following pirState'.format(self.target), 'target')
                    else:
                        self.target = self.low
                        a_print('The target light is now set to {}'.format(self.target), 'target')
                       
                    self.pir_allow(True)                
                self.lastHit = thisHit

        elif gpio == self.pir:

            if self.allowPIR == True:

                if self.pirState == False:
                    a_print('PIR Triggered: It\'s been {} seconds since the last trigger. Flipping self.pirState'.format(time_delta/1000), 'input')                    
                    a_print('The PIR state is {}'.format(self.pirState), 'alert')
                 
                    self.pirState = True
                    a_print('The PIR state is now  {}'.format(self.pirState), 'alert')

                    self.target = self.high
                    a_print('The target light is now set to {}'.format(self.target), 'target')

                    self.pirHit = thisHit

                else:
                    a_print('PIR Triggered: PIR state is already {}'.format(self.pirState) ,'input')
                    self.pirHit = thisHit


            else:
                a_print('PIR triggered, but buttonState is True, resetting PIR hit time', 'input')

                self.pirHit = thisHit
                a_print('pirHit = {}'.format(self.pirHit), 'alert')
                self.pirState = True

    def pir_allow(self, state):
        a_print('PIR eligibility is: {}'.format(self.allowPIR), 'setting')
        self.allowPIR = state
        a_print('PIR eligibility is now: {}'.format(self.allowPIR), 'setting')      

    def flip_button(self):
        a_print('The button state is: {}'.format(self.buttonState), 'setting')
        self.buttonState = not self.buttonState
        a_print('The button state is now: {}'.format(self.buttonState), 'setting')

    def input_update(self):
        now = int(round(time.time() * 1000))
        if self.buttonState:
            if((now - self.lastHit) >= self.buttonMaxOnTime):
                a_print('Button was turned on {} seconds ago, turning light down.'.format(self.buttonMaxOnTime/1000), 'auto_off')

                self.flip_button()

                if self.pirState == True:
                    self.target = self.high
                    a_print('The target light is now set to {}, following pirState'.format(self.target), 'target')
                else:
                    self.target = self.low
                    a_print('The target light is now set to {}'.format(self.target), 'target')

        if self.pirState and self.allowPIR:
            delta = now - self.pirHit
            if(delta >= self.pirMaxOnTime):

                a_print('PIR was turned on over {} seconds ago, turning light down.'.format(self.pirMaxOnTime/1000), 'auto_off')
                a_print('The PIR state is {}'.format(self.pirState), 'setting')
                self.pirState = not self.pirState
                a_print('The PIR state is now {}'.format(self.pirState), 'setting')
                self.target = self.low
                a_print('The target light is now set to {}'.format(self.target), 'target')

    def fade(self, target, pin):
        try:
            current = self.pi.get_PWM_dutycycle(pin)
            a_print('Light setting entering fade is {}'.format(current), 'alert')
        except:
            current = 0
            a_print('Caught Exception, set current light to {}'.format(current), 'alert')

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

        a_print('Light setting exiting fade is {}'.format(target), 'alert')


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

        # a_print('self.on_time: {} | self.off_time: {} | now: {}'.format(self.on_time, self.off_time, now), 'alert')

        if now >= self.on_time and now <= self.off_time:
            self.low = settings_object.low 
            self.high = settings_object.high 
        elif now < self.on_time or now > self.off_time:
            self.low = 0 
            self.high = settings_object.low 

        self.manual = settings_object.manual

        if boot:
            self.target = self.low
            a_print('Booting - Setting initial target to {}'.format(self.target), 'alert')
        else:
            pass

        if self.buttonState:
            self.target = self.manual
        elif self.pirState:
            self.target = self.high
        else:
            self.target = self.low

    def main(self):
        self.update_settings(historical_settings[-1])
        # a_print(str(historical_settings[-1]), 'alert')
        self.input_update()
        self.set_light()