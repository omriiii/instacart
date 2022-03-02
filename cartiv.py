
import json
import dbmanager
from flask import Flask, session, request, render_template, flash, redirect
import time
import utilities

import notifier

class Cartiv:
    def __init__(self, config_fname):
        self.config = self.__load_config(config_fname)
        self.app = self.__load_service()
        self.app.config['SECRET_KEY'] = 'super secret key'
        self.notifier = notifier.Notifier()

        db = self.getDbManager()
        db.init_db()
        db.con.close()

        self.token_lookup = {}

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

        @app.route("/", methods=['GET'])
        def index():
            if 'session_token' in session:
                #https://testdriven.io/blog/flask-sessions/

                if session["session_token"] not in self.token_lookup:
                    del session["session_token"]
                    return "Token doesn't exist. Please re-login", 500
                if (self.token_lookup[session["session_token"]][1]+86400 < time.time()):
                    del session["session_token"]
                    return "Token expire. Please re-login", 500

                """
                db = self.getDbManager()
                user = db.get_user_metedata(self.token_lookup[session["session_token"]][0])
                db.con.close()
                """
                username = self.token_lookup[session["session_token"]][0]

                db = self.getDbManager()
                user_groups = db.get_user_groups(username)
                db.con.close()

                if(len(user_groups) == 0):
                    return render_template("groupless_app.html", display_name=username)

                return render_template("app.html", display_name=username)

            else: #home page here?
                return "<a href=\"/register\">register</a> <a href=\"/login\">login</a>"

        @app.route("/about", methods = ['GET'])
        def about():
            return "<h1>This is the about page!</h1>"

        @app.route("/login", methods = ['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                new_db = self.getDbManager()

                if new_db.auth(username, password):
                    #flash('Login successfully!', category = 'success')
                    session["session_token"] = utilities.make_random_string()
                    self.token_lookup[session["session_token"]] = (username, time.time())
                    return redirect("/")
                else:
                    flash('Login failed', category = 'error')
                    return redirect("/login")
            elif request.method == 'GET':
                return render_template("login.html", boolean=True)

        @app.route("/make_group", methods = ['POST'])
        def make_group():
            if request.method == 'POST':
                group_name = request.form.get('group_name')
                username = self.token_lookup[session["session_token"]][0]
                new_db = self.getDbManager()
                row = new_db.group_exists(group_name)
                if row:
                    flash('Group\'s name is already taken...', category='error')
                elif not group_name:
                    flash('Please fill in group\'s name fields', category='error')
                elif len(group_name) < 4:
                    flash('Group\'s name must be greater than 4 characters.', category='error')
                else:
                    new_db.make_group(group_name, username)
                    #flash('Group created successfully!', category = 'success')
                    return redirect("/")

            return render_template('groupless_app.html', display_name = username)
            #print("make_group() called")
            # Make Group Here!!
            # Send packet back to user to refresh page

        @app.route("/join_group", methods = ['POST', 'GET'])
        def join_group():
            if request.method == 'POST':
                group_id = request.form.get('group_id')
                new_db = self.getDbManager()
                username = self.token_lookup[session["session_token"]][0]
                if not new_db.group_exists_by_id(group_id):
                    flash('The group does not exist.', category='error')
                else:
                    if new_db.group_membership_exists(username, group_id):
                        flash('You already in the group!', category = 'error')

                    else:
                        new_db.join_group(username, group_id)
                        flash('Joined Group successfully', category='success')
                        return redirect("/")

            return render_template('groupless_app.html', display_name = username)

            # print("join_group() called")
            # Join Group Here!
            # Send packet back to user to refresh page

        @app.route("/register", methods = ['POST', 'GET'])
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
                    return redirect("/")

            return render_template("register.html", boolean = True)
        # Add "Update shopping list" post request endpoint here

        return app

    #
    #   Instantiate backend REST API
    def run(self):
        self.app.run()