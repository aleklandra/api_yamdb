import csv
import sqlite3
import os


cwd = os.getcwd()
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
data = os.listdir(cwd + '//static//data')

for file in data:
    with open(f'{cwd}/static/data//{file}', 'r', encoding="utf8") as f:
        dict_file = csv.reader(f, delimiter=',')
        headers = next(dict_file)
        result = []
        for row in dict_file:
            t = ()
            for i in range(len(headers)):
                t = t + (row[i], )
            result.append(t)
    string_headers = ', '.join(headers)
    questions = ', '.join(['?' for col in headers])
    insert = (f'INSERT OR IGNORE INTO reviews_{file[:-4]} ({string_headers}) '
              f'VALUES ({questions});')
    cur.executemany(insert, result)
    con.commit()
con.close()
