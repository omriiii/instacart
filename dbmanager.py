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
        self.c.execute(''' CREATE TABLE IF NOT EXISTS users(
                            username                   TEXT PRIMARY KEY NOT NULL,
                            firstName                  TEXT NOT NULL, 
                            lastName                   TEXT NOT NULL, 
                            password                   TEXT NOT NULL,
                            email                      TEXT NOT NULL, 
                            salt                       TEXT);''')

        self.c.execute(''' CREATE TABLE IF NOT EXISTS groups(
                            group_name      TEXT, 
                            pfp_url         TEXT);''')

        """
        self.c.execute('''CREATE TABLE IF NOT EXISTS group_membership(
                            username INT NOT NULL,
                            group_name INT NOT NULL,
                            PRIMARY KEY (username, group_name),
                            CONSTRAINT FOREIGN KEY (username) REFERENCES users (username),
                            CONSTRAINT FOREIGN KEY (group_name) REFERENCES groups (group_name)''')
        """

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def make_random_salt(self):
        return ''.join(random.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits) for _ in range(256))

    def add_user(self, username, firstName, lastName, password, email):
        salt = self.make_random_salt()
        hashed_password = self.hash_password(password+salt)
        self.c.execute("INSERT INTO users_login VALUES (?, ?, ?, ?, ?, ?)", (username, firstName, lastName, hashed_password, email, salt))
        self.con.commit()

    def get_user_metedata(self, username):
        keys = ["username", "group_id", "display_name", "pfp_url"]
        self.c.execute("SELECT username, group_id, display_name, pfp_url FROM users WHERE username == ?", (username,))
        d = self.c.fetchall()

        if len(d) == 0:
            return None

        return { keys[t[0]]:t[1] for t in enumerate(d[0]) }

    def get_users(self):
        self.c.execute("SELECT * FROM users_login")
        rows = self.c.fetchall()
        return rows

    def auth(self, username, password):
        self.c.execute("SELECT username FROM users_login WHERE username = ? AND password = ?", (username, password))
        row = self.c.fetchone()
        return row

    def check_duplication(self, username):
        self.c.execute("SELECT * FROM users_login WHERE username=?", (username,))
        return self.c.fetchone()

    def delete_user(self, username):
        self.c.execute("DELETE FROM users_login WHERE username = ?", (username,))
        self.con.commit()

