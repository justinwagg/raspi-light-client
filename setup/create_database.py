
import sqlite3
import os

try:
    os.remove('../settings.db')
    print('Deleted')
except OSError:
	print('Error')

conn = sqlite3.connect('../settings.db')
c = conn.cursor()

settings = 'create table if not exists settings ( `device_id` INTEGER, `on_time` TEXT, `low_time` TEXT, `off_time` TEXT, `low` INTEGER, `high` INTEGER, `manual` INTEGER, `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `received_on` TEXT );'
c.execute(settings)


insert_query = "insert into settings (device_id, on_time, low_time, off_time, low, high, manual, received_on)  VALUES ('1', '17:00:00', '23:59:00', '07:30:00', '30', '75', '100', '2018-03-03 13:45:54.163483');"

c.execute(insert_query)
conn.commit()

conn.close()