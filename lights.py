import pigpio
import time
from printer import a_print
import datetime
from settings import historical_settings, getLastSettings
from config import Config
import sys


class Lights(object):

    def __init__(self):
        self.led_array = Config.led_array
        self.switch = Config.switch
        self.pir = Config.pir
        self.pi = pigpio.pi()

        self.pi.set_mode(self.switch, pigpio.INPUT)

        self.pi.set_mode(self.pir, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pir, pigpio.PUD_DOWN)

        self.pi.set_mode(self.led_array, pigpio.OUTPUT)

        self.buttonState = False
        self.buttonMaxOnTime = Config.buttonMaxOnTime

        self.pirState = False
        self.allowPIR = True

        self.pirMaxOnTime = Config.pirMaxOnTime

        self.currentLight = None
        self.lastHit = int(round(time.time() * 1000)) - 1000
        self.pirHit = self.lastHit

        # Settings
        self.off = None
        self.low = None
        self.high = None
        self.manual = None
        self.on_time = None
        self.low_time = None
        self.off_time = None
        self.time_block = None

        self.target = self.low

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

    def update_settings(self, historical_settings, boot=False):
        # The job of update_settings is to figure out where in the day we are (off, low, high).
        # I'm creating a list of times to find out which one we're between, this is tricky because times can span midnight

        self.on_time = historical_settings.on_time
        self.low_time = historical_settings.low_time
        self.off_time = historical_settings.off_time

        settings_dict = historical_settings.__dict__

        settings_dt = []
        times = [self.on_time, self.off_time, self.low_time]
        today = datetime.datetime.today()
        for i in range(-1,2):
            for j in range(len(times)):
                settings_dt.append(
                    datetime.datetime.combine(today + datetime.timedelta(days=i), times[j])
                    )
        settings_dt = sorted(settings_dt)

        now = datetime.datetime.now()
        for i in range(len(settings_dt)):
            if now >= settings_dt[i] and now < settings_dt[i+1]:
                self.low = settings_dict['mode_config'][str(settings_dt[i].time())]['low']
                self.high = settings_dict['mode_config'][str(settings_dt[i].time())]['high']
                self.manual = settings_dict['mode_config'][str(settings_dt[i].time())]['manual']
                self.off = settings_dict['mode_config'][str(settings_dt[i].time())]['off']

                if self.time_block != str(settings_dt[i].time()):
                    a_print('Time block change - Time block was: {}'.format(self.time_block), 'setting')
                    self.time_block = str(settings_dt[i].time())
                    a_print('Time block change - Time is: {}'.format(self.time_block), 'setting')

        if boot:
            self.target = self.low
            a_print('Booting - Setting initial target to {}'.format(self.target), 'alert')
            # a_print('Time block on Boot = {}'.format(self.time_block), 'alert')
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
        self.input_update()
        self.set_light()
