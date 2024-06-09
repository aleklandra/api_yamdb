import csv
import sqlite3
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Insert csv into data model'

    def handle(self, *args, **options):
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        data = os.listdir('.//static//data')

        for file in data:
            with open(f'.//static//data//{file}', 'r', encoding="utf8") as f:
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
            insert = (f'INSERT OR IGNORE INTO reviews_{file[:-4]} '
                      f'({string_headers}) VALUES ({questions});')
            cur.executemany(insert, result)
            con.commit()
        con.close()
