import sqlite3

conn = sqlite3.connect('stat.sqlite')

c = conn.cursor()

c.execute('''
          DROP TABLE stats
          ''')

conn.commit()
conn.close()