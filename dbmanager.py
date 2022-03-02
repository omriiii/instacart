import sqlite3
import utilities
import hashlib

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
                            salted_hashed_password     TEXT NOT NULL,
                            salt                       TEXT NOT NULL,
                            email                      TEXT NOT NULL,
                            firstName                  TEXT NOT NULL, 
                            lastName                   TEXT NOT NULL,
                            pfp_url                    TEXT);''')

        self.c.execute(''' CREATE TABLE IF NOT EXISTS groups(
                                    group_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                    group_name      TEXT, 
                                    pfp_url         TEXT);''')


        self.c.execute('''CREATE TABLE IF NOT EXISTS group_membership(
                                    username    TEXT NOT NULL,
                                    group_id    INT NOT NULL,
                                    PRIMARY KEY (username, group_id),
                                    CONSTRAINT c1 FOREIGN KEY (username) REFERENCES users (username),
                                    CONSTRAINT c2 FOREIGN KEY (group_id) REFERENCES groups (group_id))''')


    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, firstName, lastName, password, email):
        salt = utilities.make_random_string()
        salted_hashed_password = self.hash_password(password+salt)
        self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (username, salted_hashed_password, salt, email, firstName, lastName, ""))
        self.con.commit()

    def get_user_metedata(self, username):
        self.c.execute("SELECT firstName, lastName, pfp_url FROM users WHERE username == ?", (username,))
        return self.c.fetchone()

    def get_user_groups(self, username):
        self.c.execute("SELECT group_id FROM group_membership WHERE username == ?", (username,))
        return self.c.fetchall()

    def get_users(self):
        self.c.execute("SELECT * FROM users")
        rows = self.c.fetchall()
        return rows

    def auth(self, username, password):
        if self.user_exists(username):
            self.c.execute("SELECT salted_hashed_password, salt FROM users WHERE username = ?", (username,))
            row = self.c.fetchone()
            return self.hash_password(password+row["salt"]) == row["salted_hashed_password"]
        else:
            return None

    def user_exists(self, username):
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.c.fetchone()

    def delete_user(self, username):
        self.c.execute("DELETE FROM users WHERE username = ?", (username,))
        self.con.commit()

    # apply function overloading later
    def group_exists(self, group_name):
        self.c.execute("SELECT * FROM groups WHERE group_name=?", (group_name, ))
        return self.c.fetchone()

    # apply function overloading later
    def group_exists_by_id(self, group_id):
        self.c.execute("SELECT * FROM groups WHERE group_id=?", (group_id,))
        return self.c.fetchone()

    def count_groups(self):
        self.c.execute("SELECT COUNT(*) FROM groups")
        return self.c.fetchone()[0]

    def make_group(self, group_name, username):
        self.c.execute("INSERT INTO groups (group_name, pfp_url) VALUES (?,?)", (group_name, ""))
        self.con.commit()
        self.c.execute("SELECT group_id FROM groups WHERE group_name = ?", (group_name,))
        group_id = self.c.fetchone()["group_id"]
        self.c.execute("INSERT INTO group_membership VALUES (?, ?)", (username, group_id))
        self.con.commit()


    def group_membership_exists(self, username, group_id):
        self.c.execute("SELECT * FROM group_membership WHERE username=? AND group_id=?", (username, group_id))
        return self.c.fetchone()

    def join_group(self, username, group_id):
        self.c.execute("INSERT INTO group_membership VALUES (?,?)", (username, group_id))
        self.con.commit()



