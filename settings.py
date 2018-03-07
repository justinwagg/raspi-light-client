
import datetime
import sqlite3


class Settings(object):
    def __init__(self, settings_dict, insert=False):

        settings_dict['received_on'] = datetime.datetime.now() if 'received_on' not in settings_dict else settings_dict['received_on']

        self.low = settings_dict['low'] if 'low' in settings_dict else None
        self.high = settings_dict['high'] if 'high' in settings_dict else None
        self.manual = settings_dict['manual'] if 'manual' in settings_dict else None
        self.on_time = datetime.datetime.strptime(settings_dict['on_time'], '%H:%M:%S').time() if 'on_time' in settings_dict else None
        self.off_time = datetime.datetime.strptime(settings_dict['off_time'], '%H:%M:%S').time() if 'off_time' in settings_dict else None
        self.received_on = datetime.datetime.strptime(settings_dict['received_on'], '%Y-%m-%d %H:%M:%S.%f') if 'recieved_on' in settings_dict else datetime.datetime.now()

        if insert:
            settings_dict.pop('csrf_token')
            settings_dict.pop('submit')
            settings_dict['device_id'] = settings_dict['device']
            settings_dict.pop('device')

            print('Saving Record in SQLite')
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
        return 'On Time: {0:%I:%M %p} | Off Time: {1:%I:%M %p} | Low Light: {2}% | High Light: {3}% | Manual Light: {4}% | As of: {5:%Y-%m-%d %I:%M %p}'.format(self.on_time, self.off_time, self.low, self.high, self.manual, self.received_on)