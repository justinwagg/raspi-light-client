
import sqlite3
import os

try:
    os.remove('settings.db')
    print('Deleted')
except OSError:
    pass

conn = sqlite3.connect('settings.db', check_same_thread=False)
c = conn.cursor()

c.execute('drop table if exists settings;')
conn.commit()

settings = 'create table settings ( `device_id` INTEGER, `on_time` TEXT, `off_time` TEXT, `low` INTEGER, `high` INTEGER, `manual` INTEGER, `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `received_on` TEXT );'
c.execute(settings)
conn.commit()

insert_query = "insert into settings (device_id, on_time, off_time, low, high, manual, received_on)  VALUES ('1', '17:00:00', '23:00:00', '30', '75', '100', '2018-03-03 13:45:54.163483');"

c.execute(settings)
conn.commit()

conn.close()