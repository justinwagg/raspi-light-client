
class Config:

    # GPIO Input/Output (lights.py)
    led_array = 27
    switch = 4
    pir = 17

    # Settings (lights.py)
    buttonMaxOnTime = 1200000 # Seconds to auto shut off light after manual turn on
    pirMaxOnTime = 120000 # Seconds to auto shut off light after PIR turn on

    # Log location (printer.py)
    log_on = True
    log = 'logs/main.log'

    # mqtt
    broker = '192.168.1.55'
    topic = 'lights.bathroom'
