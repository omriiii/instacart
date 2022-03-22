import sqlite3
import utilities
import hashlib
import time

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
        self.c.execute(''' CREATE TABLE users(
                            username                   TEXT PRIMARY KEY NOT NULL,
                            salted_hashed_password     TEXT NOT NULL,
                            salt                       TEXT NOT NULL,
                            email                      TEXT NOT NULL,
                            firstName                  TEXT NOT NULL, 
                            lastName                   TEXT NOT NULL,
                            pfp_url                    TEXT);''')

        self.c.execute(''' CREATE TABLE groups(
                                    group_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                    group_name      TEXT, 
                                    pfp_url         TEXT);''')

        self.c.execute('''CREATE TABLE group_membership(
                                    username    TEXT NOT NULL,
                                    group_id    INT NOT NULL,
                                    PRIMARY KEY (username, group_id),
                                    CONSTRAINT c1 FOREIGN KEY (username) REFERENCES users (username),
                                    CONSTRAINT c2 FOREIGN KEY (group_id) REFERENCES groups (group_id))''')

        self.c.execute('''CREATE TABLE default_shopping_items(
                                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name        TEXT,
                                    img_url     TEXT)''')

        # Some arbitrary items.
        # Should probs instantiate from existing database?
        # Looks up using Kaggle or something
        #
        # Maybe download this csv https://data.nal.usda.gov/dataset/usda-branded-food-products-database
        # and write scraper to download an image for each item?
        items = [("Apple", "https://media.istockphoto.com/photos/red-apple-picture-id184276818?k=20&m=184276818&s=612x612&w=0&h=QxOcueqAUVTdiJ7DVoCu-BkNCIuwliPEgtAQhgvBA_g="),
                 ("Banana", "https://bakingmischief.com/wp-content/uploads/2022/01/banana-recipes-image-square.jpg"),
                 ("Kiwi", "https://images.immediate.co.uk/production/volatile/sites/30/2020/02/Kiwi-fruits-582a07b.jpg?quality=90&resize=504,458")]

        self.c.executemany("INSERT INTO default_shopping_items(name, img_url) VALUES (?, ?)", items)

        self.con.commit()


    def hash(self, s):
        return hashlib.sha512(s.encode()).hexdigest()

    def add_user(self, username, firstName, lastName, password, email):
        salt = utilities.make_random_string()
        salted_hashed_password = self.hash(password + salt)
        self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (username, salted_hashed_password, salt, email, firstName, lastName, ""))
        self.con.commit()

    def get_user_metedata(self, username):
        self.c.execute("SELECT firstName, lastName, pfp_url FROM users WHERE username == ?", (username,))
        return self.c.fetchone()

    def getUsersGroups(self, username):
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
            return self.hash(password + row["salt"]) == row["salted_hashed_password"]
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
        self.c.execute("CREATE TABLE group_" + str(group_id) + "_items" + '''(
                                    id         INT NOT NULL,
                                    is_custom_item  INT NOT NULL,
                                    quantity        INT DEFAULT 1)''')

        self.con.commit()

    def getGroupItems(self, group_id):
        self.c.execute("SELECT * FROM group_" + str(group_id) + "_items")
        return [{"id": t[0], "quantity": t[2]} for t in self.c.fetchall()]

    def addItemToGroup(self, group_id, item_id):
        self.c.execute("SELECT count(*) FROM group_" + str(group_id) + "_items WHERE id==" + item_id)
        c = self.c.fetchone()[0]
        if(c == 0):
            self.c.execute("INSERT INTO group_" + str(group_id) + "_items VALUES(?, ?, ?)", (item_id, 0, 1))
        else:
            self.c.execute("UPDATE group_" + str(group_id) + "_items SET quantity = quantity+1 WHERE id==" + item_id)
        self.con.commit()
        return True

    def getItemData(self, item_id):
        if type(item_id) == list:
            self.c.execute("SELECT * FROM default_shopping_items WHERE id IN " + getSQLiteList(item_id))
            return self.c.fetchall()

        self.c.execute("SELECT * FROM default_shopping_items WHERE id==" + item_id)
        return self.c.fetchone()


    def group_membership_exists(self, username, group_id):
        self.c.execute("SELECT * FROM group_membership WHERE username=? AND group_id=?", (username, group_id))
        return self.c.fetchone()

    def join_group(self, username, group_id):
        self.c.execute("INSERT INTO group_membership VALUES (?,?)", (username, group_id))
        self.con.commit()

    def get_addble_shopping_times(self):
        self.c.execute("SELECT * FROM default_shopping_items")
        return self.c.fetchall()

    def get_tables_cnt(self):
        self.c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name != 'android_metadata' AND name != 'sqlite_sequence';")
        return self.c.fetchone()[0]


def getSQLiteList(l):
    return "(" + ", ".join(["\"" + str(s) + "\"" for s in l]) + ")"

def SQLiteRowToDict(d):
    return dict(zip(d.keys(), d))