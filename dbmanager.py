import sqlite3
import json
import hashlib
import random
import string

"""
Stolen from https://realpython.com/prevent-python-sql-injection/

# BAD EXAMPLES. DON'T DO THIS!
cursor.execute("SELECT admin FROM users WHERE username = '" + username + '");
cursor.execute("SELECT admin FROM users WHERE username = '%s' % username);
cursor.execute("SELECT admin FROM users WHERE username = '{}'".format(username));
cursor.execute(f"SELECT admin FROM users WHERE username = '{username}'");

# SAFE EXAMPLES. DO THIS!
cursor.execute("SELECT admin FROM users WHERE username = ?", (username, ));
cursor.execute("SELECT admin FROM users WHERE username = %(username)s", {'username': username});

"""



class db:
    def __init__(self, fname):
        self.con = sqlite3.connect(fname)
        self.con.row_factory = sqlite3.Row
        self.c = self.con.cursor()

    def init_db(self):
        self.c.execute(''' CREATE TABLE IF NOT EXISTS users_login(
                            username                   TEXT PRIMARY KEY, 
                            password                   TEXT,
                            salt                       TEXT);''')

        self.c.execute(''' CREATE TABLE IF NOT EXISTS users(
                            username        TEXT PRIMARY KEY, 
                            group_id        INT DEFAULT NULL,
                            display_name    TEXT,
                            pfp_url         TEXT);''')

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def make_random_salt(self):
        return ''.join(random.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits) for _ in range(256))

    def add_user(self, username, password):
        hashed_password = self.hash_password(password)
        salt = self.make_random_salt()
        self.c.execute("INSERT INTO user_login (username, password, salt) VALUES (%s, %s, %s)", (username,  hashed_password, salt))

    def get_user_metedata(self, username):

        keys = ["username", "group_id", "display_name", "pfp_url"]
        self.c.execute("SELECT username, group_id, display_name, pfp_url FROM users WHERE username == ?", (username,))
        d = self.c.fetchall()

        if len(d) == 0:
            return None

        return { keys[t[0]]:t[1] for t in enumerate(d[0]) }