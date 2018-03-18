
import datetime
import sqlite3
from printer import a_print

historical_settings = []

class Settings(object):
    def __init__(self, settings_dict, insert=False):

        settings_dict['received_on'] = datetime.datetime.now() if 'received_on' not in settings_dict else settings_dict['received_on']

        self.low = settings_dict['low'] if 'low' in settings_dict else None
        self.high = settings_dict['high'] if 'high' in settings_dict else None
        self.manual = settings_dict['manual'] if 'manual' in settings_dict else None
        self.on_time = datetime.datetime.strptime(settings_dict['on_time'], '%H:%M:%S').time() if 'on_time' in settings_dict else None
        self.low_time = datetime.datetime.strptime(settings_dict['low_time'], '%H:%M:%S').time() if 'low_time' in settings_dict else None
        self.off_time = datetime.datetime.strptime(settings_dict['off_time'], '%H:%M:%S').time() if 'off_time' in settings_dict else None
        self.received_on = datetime.datetime.strptime(settings_dict['received_on'], '%Y-%m-%d %H:%M:%S.%f') if 'recieved_on' in settings_dict else datetime.datetime.now()

        self.mode_config = {
            settings_dict['off_time'] : {'off': 0, 'low': 0, 'high': 0, 'manual': self.manual },
            settings_dict['low_time'] : {'off': 0, 'low': 0, 'high': self.low, 'manual': self.manual },
            settings_dict['on_time'] : {'off': 0, 'low': self.low, 'high': self.high, 'manual': self.manual },
        }

        if insert:
            settings_dict.pop('csrf_token')
            settings_dict.pop('submit')
            settings_dict['device_id'] = settings_dict['device']
            settings_dict.pop('device')

            a_print('Saving Record in SQLite', 'sql')
            conn = sqlite3.connect('settings.db', check_same_thread=False)
            c = conn.cursor()
            table = 'settings'
            cols = ', '.join('"{}"'.format(col) for col in settings_dict.keys())
            vals = ', '.join("'{}'".format(col) for col in settings_dict.values())
            sql = 'INSERT INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
            c.execute(sql, settings_dict)
            conn.commit()
            conn.close()

        print(self)

    def __repr__(self):
        # return 'On Time: {self.on_time:%I:%M %p} | Off Time: {self.off_time:%I:%M %p} | Low Light: {self.low}% | High Light: {self.high}% | Manual Light: {self.manual}% | As of: {self.received_on:%Y-%m-%d %I:%M %p}'.format(self.on_time, self.off_time, self.low, self.high, self.manual, self.received_on)
        return 'On Time: {0:%I:%M %p} | Low Time: {1:%I:%M %p} | Off Time: {2:%I:%M %p} | Low Light: {3}% | High Light: {4}% | Manual Light: {5}% | As of: {6:%Y-%m-%d %I:%M %p}'.format(self.on_time, self.low_time, self.off_time, self.low, self.high, self.manual, self.received_on)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def getLastSettings():
    # print('No settings, getting defaults from SQLite')
    a_print('No settings, getting defaults from SQLite', 'setting')
    try:
        conn = sqlite3.connect('settings.db', check_same_thread=False)
        c = conn.cursor()
        c.row_factory = dict_factory
        c.execute('select high, low, manual, off_time, low_time, on_time, received_on from settings a inner join (select max(id) as id from settings) b on a.id=b.id')
        results = c.fetchall()
        conn.close()
        historical_settings.append(Settings(results[0]))
    except:
        default = {
            'low': 30,
            'high': 100,
            'manual': 100,
            'on_time': '17:00:00',
            'low_time': '23:59:00',
            'off_time': '07:30:00',
        }
        historical_settings.append(Settings(default))


