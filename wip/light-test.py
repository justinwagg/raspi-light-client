import pigpio
import time
import re
import datetime

class Lights(object):
    def __init__(self):
        # GPIO
        self.switch = 4
        self.pir = 17
        self.led_array = 27
        self.pi = pigpio.pi()
        self.pi.set_mode(self.switch, pigpio.INPUT)
        self.pi.set_pull_up_down(self.switch, pigpio.PUD_DOWN)
        self.pi.set_mode(self.pir, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pir, pigpio.PUD_DOWN)
        self.pi.set_mode(self.led_array, pigpio.INPUT)

        # State Tracking
        self.buttonState = False
        self.pirState = False
        self.allowPIR = True

        # Time keeping
        self.lastHit = int(round(time.time() * 1000)) - 5000

        # Light Settings
        self.low = 30 
        self.high = 100
        self.manual = 255        
        self.on_time = datetime.datetime.strptime('12:00:00', '%H:%M:%S').time()
        self.off_time = datetime.datetime.strptime('23:00:00', '%H:%M:%S').time()
        self.default = 100
        self.target = self.default

    def event_cbf(self, gpio, level, tick):
        thisHit = int(round(time.time() * 1000))
        time_delta = thisHit - self.lastHit

        if gpio == self.switch:
            if(time_delta >= 1000):
                self.a_print('Button Pressed: It\'s been {} seconds since the last input. Flipping self.buttonState.'.format(time_delta/1000), 'input')
                print(gpio, level, tick)
                self.flip_button()
                self.lastHit = thisHit

            # If the light is now to be on    
            if self.buttonState == True:
                self.target = self.manual
                self.a_print('The target light is now set to {}'.format(self.target), 'target')
                self.pir_allow(False)

            # If the light is now to be off 
            elif self.buttonState == False:
                    if self.pirState == True:
                        self.target = self.high
                        self.a_print('The target light is now set to {}, following pirState'.format(self.target), 'target')
                    else:
                        self.target = self.default
                        self.a_print('The target light is now set to {}'.format(self.target), 'target')                

        elif gpio == self.pir:
            self.a_print('PIR hit', 'alert')
            print(gpio, level, tick)

    def flip_button(self):
        self.a_print('The button state is: {}'.format(self.buttonState), 'setting')
        self.buttonState = not self.buttonState
        self.a_print('The button state is now: {}'.format(self.buttonState), 'setting')

    def pir_allow(self, state):
        self.a_print('PIR eligibility is: {}'.format(self.allowPIR), 'setting')
        self.allowPIR = state
        self.a_print('PIR eligibility is now: {}'.format(self.allowPIR), 'setting')  

    def a_print(self, string, level):
        x = {
        'setting': '\x1b[30;41mSetting Change\x1b[0m: ',
        'target': '\x1b[30;42mTarget Change\x1b[0m: ',
        'alert': '\x1b[31;40mAlert\x1b[0m: ',
        'auto_off': '\x1b[30;44mAUTO OFF ALERT\x1b[0m: ',
        'input': '\x1b[30;42mINPUT\x1b[0m: '
        }
        fixed = re.sub('True', '\x1b[32;40mTrue\x1b[0m', string)
        fixed = re.sub('False', '\x1b[31;40mFalse\x1b[0m', fixed)
        print(x[level] + fixed)

lights = Lights()

cb1 = lights.pi.callback(lights.switch, pigpio.RISING_EDGE, lights.event_cbf)
cb2 = lights.pi.callback(lights.pir, pigpio.RISING_EDGE, lights.event_cbf)

try:
    while True:
        pass

except KeyboardInterrupt:
    lights.pi.set_PWM_dutycycle(lights.led_array, 0)
    lights.pi.stop()