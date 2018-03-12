import re
import datetime
import logging

logging.basicConfig(filename='main.log', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)

def a_print(string, level):
    x = {
        'setting': ' \x1b[30;41mSetting\x1b[0m: ',
        'target': ' \x1b[30;42mTarget\x1b[0m: ',
        'alert': ' \x1b[31;40mAlert\x1b[0m: ',
        'auto_off': ' \x1b[30;44mAUTO OFF\x1b[0m: ',
        'input': ' \x1b[30;42mINPUT\x1b[0m: ',
        'mqtt': ' \x1b[33;40mMQTT\x1b[0m: ',
        'sql': ' \x1b[34;40mSQL\x1b[0m: '
    }
    fixed = re.sub('True', '\x1b[32;40mTrue\x1b[0m', string)
    fixed = re.sub('False', '\x1b[31;40mFalse\x1b[0m', fixed)
    print(str(datetime.datetime.now()) + x[level] + fixed)
    logging.debug(string)