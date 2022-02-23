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
cursor.execute("SELECT admin FROM users WHERE username = %s'", (username, ));
cursor.execute("SELECT admin FROM users WHERE username = %(username)s", {'username': username});

"""



class db:
    def __init__(self, fname):
        self.con = sqlite3.connect(fname)
        self.c = self.con.cursor()
        self.__init_db()

    def __init_db(self):
        self.c.execute(''' CREATE TABLE IF NOT EXISTS users(
                            username                   TEXT PRIMARY KEY NOT NULL,
                            group_id                   INT DEFAULT NULL,
                            firstName                  TEXT NOT NULL, 
                            lastName                   TEXT NOT NULL, 
                            password                   TEXT NOT NULL,
                            email                      TEXT NOT NULL, 
                            salt                       TEXT);''')

        self.c.execute(''' CREATE TABLE IF NOT EXISTS groups(
                            group_name      TEXT PRIMARY KEY, 
                            group_id        INT DEFAULT NULL,
                            pfp_url         TEXT);''')

        '''self.c.execute('''CREATE TABLE IF NOT EXISTS group_membership(
                            username TEXT NOT NULL,
                            group_id INT NOT NULL,
                            PRIMARY KEY (username, group_id),
                            CONSTRAINT FOREIGN KEY (username) REFERENCES users (username),
                            CONSTRAINT FOREIGN KEY (group_id) REFERENCES groups (group_id)''')
        '''


    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def make_random_salt(self):
        return ''.join(random.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits) for _ in range(256))

    def add_user(self, username, firstName, lastName, password, email):
        hashed_password = self.hash_password(password)
        salt = self.make_random_salt()
        self.c.execute("INSERT INTO users_login VALUES (?, ?, ?, ?, ?, ?)", (username, firstName, lastName, hashed_password, email, salt))
        self.con.commit()

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

