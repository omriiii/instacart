import sqlite3
import json


class db:
    def __init__(self, fname):
        self.con = sqlite3.connect(fname)
        self.c = self.con.cursor()
        self.__init_db()

    def __init_db(self):

        self.c.execute(''' CREATE TABLE IF NOT EXISTS users_login(
                            username                   TEXT PRIMARY KEY, 
                            password                   TEXT,
                            salt                       TEXT);''')

        self.c.execute(''' CREATE TABLE IF NOT EXISTS users(
                            username        TEXT PRIMARY KEY, 
                            group_id        TEXT,
                            display_name    TEXT,
                            pfp_url         TEXT);''')