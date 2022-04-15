
import json
import dbmanager
from dbmanager import SQLiteRowToDict
from flask import Flask, session, request, render_template, flash, redirect, send_from_directory, abort
import time
import utilities
import notifier
import pytumblr

class Cartiv:
    def __init__(self, config_fname):
        self.config = self.__load_config(config_fname)
        self.app = self.__load_service()
        self.app.config['SECRET_KEY'] = 'super secret key'

        self.notifier = notifier.Notifier()
        self.token_lookup = {}

        db = self.getDbManager()
        if db.get_tables_cnt() == 0:
            db.init_db()
        db.con.close()


    def getDbManager(self):
        return dbmanager.db(self.config["db_fname"])

    #
    #   Load config as a dictionary from a given json filepath
    def __load_config(self, config_fname):
        config_file = open(config_fname)
        return json.loads(config_file.read())

    #
    #   Load in the backend REST API
    def __load_service(self):
        app = Flask("cartiv")

        def getUser(session, token_optional=False):
            if 'session_token' in session:
                if session["session_token"] not in self.token_lookup:
                    del session["session_token"]
                    abort(401, "Session token doesn't exist. Please re-login.")
                if (self.token_lookup[session["session_token"]][1]+86400 < time.time()):
                    del session["session_token"]
                    abort(401, "Session token expire. Please re-login.")
                return self.token_lookup[session["session_token"]][0]
            elif not token_optional: # token mandatory
                abort(403, "No session token attached.")

            return False


        @app.route("/", methods=['GET'])
        def index():
            user = getUser(session, token_optional=True)
            if user:
                db = self.getDbManager()
                user_groups = db.getUsersGroups(user)
                user_groups_name = [d["group_name"] for d in db.getGroupsNames(user_groups)]
                db.con.close()
                return render_template("app.html", display_name=user, group_list=user_groups_name, group_exist=(len(user_groups) == 0))
            else:
                return render_template("home.html")

        @app.route("/home", methods=['GET'])
        def home():
            user = getUser(session, token_optional=True)
            return render_template("home.html", display_name=user)

        @app.route("/about", methods = ['GET'])
        def about():
            user = getUser(session, token_optional=True)
            return render_template("about.html", display_name=user)

        @app.route("/blog", methods=['GET'])
        def blog():
            user = getUser(session, token_optional=True)
            client = pytumblr.TumblrRestClient(
                self.config["tumblr_keys"]["consumer_key"],
                self.config["tumblr_keys"]["consumer_secret"],
                self.config["tumblr_keys"]["oauth_token"],
                self.config["tumblr_keys"]["oauth_secret"],
            )
            client.info()  # Grabs the current user information
            tumblr_posts = client.posts('cartivblog', type='text', filter='text')
            tumblr_posts = tumblr_posts.get("posts")

            posts = []
            for post in tumblr_posts:
                item = {
                    "title": post.get("title", ""),
                    "text": post.get("body", ""),
                    "url": post.get("post_url", "")
                }
                print(item)
                posts.append(item)
            print(posts)
            return posts
            #return render_template("blog.html", posts, display_name=user)
            #return render_template("blog.html", display_name=user)

        @app.route("/login", methods = ['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                new_db = self.getDbManager()

                if new_db.auth(username, password):
                    # Login succesful!!
                    session["session_token"] = utilities.make_random_string()
                    self.token_lookup[session["session_token"]] = (username, time.time())
                    return redirect("/")
                else:
                    flash('Login failed', category = 'error')
                    return redirect("/login")
            elif request.method == 'GET':
                return render_template("login.html")

        @app.route("/make_group", methods=['POST'])
        def make_group():
            user = getUser(session)
            group_name = request.form.get('group_name')
            db = self.getDbManager()
            if not group_name:
                flash('Please fill in group\'s name fields', category='error')
            elif len(group_name) < 4:
                flash('Group\'s name must be greater than 4 characters.', category='error')
            else:
                db.make_group(group_name, user)
                flash('Group created successfully!', category='success')

            return redirect("/")

        @app.route("/join_group", methods=['POST'])
        def join_group():
            user = getUser(session)
            group_id = request.form.get('group_id')
            db = self.getDbManager()
            if not db.group_exists_by_id(group_id):
                flash('The group does not exist.', category='error')
            elif db.group_membership_exists(user, group_id):
                flash('You are already in the group!', category='error')
            else:
                db.join_group(user, group_id)
                flash('Joined Group successfully', category='success')

            return redirect("/")



        @app.route("/register", methods=['POST', 'GET'])
        def register():
            if request.method == 'POST':
                firstName = request.form.get('firstName')
                lastName = request.form.get('lastName')
                username = request.form.get('username')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                email = request.form.get('email')
                db = self.getDbManager()
                row = db.user_exists(username)
                if row is not None:
                    flash('The username is already taken...', category = 'error')
                elif ((not username) or (not password1) or (not email) or (not firstName) or (not lastName)):
                    flash('Please fill in all required fields', category= 'error')
                elif len(username) < 4:
                    flash('Username must be greater than 4 characters', category='error')
                elif len(email) < 4:
                    flash('Email must be greater than 4 characters.', category = 'error')
                elif password1 != password2:
                    flash('Passwords don\'t match.', category = 'error')
                elif len(password1) < 7:
                    flash('Password must be at least 7 characters.', category = 'error')
                else:
                    db.add_user(username, firstName, lastName, password1, email)
                    flash('Account created successfully!', category = 'success')
                    return redirect("/register")

            return render_template("register.html")


        @app.route("/groupsShoppingItems")
        def getShoppingItems():
            user = getUser(session)

            db = self.getDbManager()
            user_group = db.getUsersGroups(user)
            if len(user_group) == 0:
                abort(403, "User has no group!")

            gi = db.getGroupItems(user_group[0])
            user_items = {d["id"]:d for d in gi}

            for d in [dict(zip(d.keys(), d)) for d in db.getItemData(list(user_items.keys()))]:
                user_items[d["id"]].update(d)

            return json.dumps(list(user_items.values()))

        @app.route("/addbleShoppingItems")
        def getAddbleShoppingItems():
            getUser(session) # Make sure a proper user is making this request!
            return json.dumps([dict(l) for l in self.getDbManager().get_addble_shopping_times()])



        @app.route("/addItemToList", methods = ['POST'])
        def addItemToList():
            user = getUser(session)
            item_id = request.args.get('id')
            # Verify the item the user wants to add exists !!
            group_id = self.getDbManager().getUsersGroups(user)[0]
            db = self.getDbManager()
            new_item_cnt = db.addItemToGroup(group_id, item_id)
            ret = SQLiteRowToDict(db.getItemData(item_id))
            ret["quantity"] = new_item_cnt
            return json.dumps(ret)
            #return "Failed to add item", 500


        @app.route("/removeItemFromList", methods = ['POST'])
        def removeItemFromList():
            user = getUser(session)
            item_id = request.args.get('id')
            # Verify the item the user wants to remove exists !!
            group_id = self.getDbManager().getUsersGroups(user)[0]
            db = self.getDbManager()
            new_item_cnt = db.removeItemFromGroup(group_id, item_id)
            ret = SQLiteRowToDict(db.getItemData(item_id))
            ret["quantity"] = new_item_cnt
            return json.dumps(ret)
            #return "Failed to remove item", 500




        @app.route('/static/<path:path>')
        def getStaticFile(path):
            return send_from_directory('static', path)

        @app.route("/team", methods=['GET'])
        def team():
            user = getUser(session, token_optional=True)
            return render_template("team.html", display_name=user)

        """
        # For future use when we'll allow users to access specific 
        # groups they're a part of 
        @app.route("/group/<group_name>", methods=['GET'])
        def group(group_name):

            # get items here and pass to render
            db = self.getDbManager()

            return render_template("group.html", boolean = True, display_group_name = group_name, items = "pass items here ")
        """

        @app.route("/logout")
        def logout():
            session.pop("session_token")
            return redirect("/")

        return app

    #
    #   Instantiate backend REST API
    def run(self):
        self.app.run()