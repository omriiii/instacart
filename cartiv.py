
import json
import dbmanager
from flask import Flask, session, request, render_template, flash
import time

import notifier

class Cartiv:
    def __init__(self, config_fname):
        self.config = self.__load_config(config_fname)
        self.app = self.__load_service()
        self.notifier = notifier.Notifier()

        db = self.getDbManager()
        db.init_db()
        db.con.close()

        self.token_lookup = {}
        self.app.config['SECRET_KEY'] = 'super secret key'

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

                db = self.getDbManager()
                user = db.get_user_metedata(self.token_lookup[session["session_token"]][0])
                db.con.close()

                if(user["group_id"] == None):
                    return "<p>MAKE/JOIN A GROUP PAGE HERE</p>"

                return render_template("app.html", display_name=user["display_name"])

            else:
                # Temp nonsense token for testing
                session["session_token"] = ":)"
                self.token_lookup[session["session_token"]] = ("omri", time.time())
                return "<p>I have given you a session token :)</p>"

        @app.route("/about", methods = ['GET'])
        def about():
            return "<h1>This is the about page!</h1>"

        @app.route("/login", methods = ['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                new_db = dbmanager.db('users.db')
                row = new_db.auth(username, new_db.hash_password(password))
                if row is None:
                    flash('Login failed!', category = 'error')
                else:
                    flash('Login successfully!', category = 'success')

            return render_template("login.html", boolean=True)



        @app.route("/register", methods = ['POST', 'GET'])
        def register():
            if request.method == 'POST':
                firstName = request.form.get('firstName')
                lastName = request.form.get('lastName')
                username = request.form.get('username')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                email = request.form.get('email')
                new_db = dbmanager.db('users.db')
                row = new_db.check_duplication(username)
                if row is not None:
                    flash('The username is already taken...', category = 'error')
                elif ((not firstName) or (not lastName) or (not username) or (not password1) or (not email)):
                    flash('Please fill in all required fields', category= 'error')
                elif len(firstName) < 2:
                    flash('First name must be greater than 2 characters.', category = 'error')
                elif len(lastName) < 2:
                    flash('First name must be greater than 2 characters.', category = 'error')
                elif len(email) < 4:
                    flash('Email must be greater than 4 characters.', category = 'error')
                elif password1 != password2:
                    flash('Passwords don\'t match.', category = 'error')
                elif len(password1) < 7:
                    flash('Password must be at least 7 characters.', category = 'error')
                else:
                    new_db = dbmanager.db('users.db')
                    new_db.add_user(username, firstName, lastName, password1, email)
                    flash('Account created successfully!', category = 'success')

            return render_template("register.html", boolean = True)
        # Add "Update shopping list" post request endpoint here
        return app

    #
    #   Instantiate backend REST API
    def run(self):
        self.app.run()