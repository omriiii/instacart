
import json
import dbmanager
from flask import Flask, session, request, render_template, flash

class Cartiv:
    def __init__(self, config_fname):
        self.config = self.__load_config(config_fname)
        self.db = dbmanager.db(self.config["db_fname"])
        self.app = self.__load_service()
        self.app.config['SECRET_KEY'] = 'super secret key'


    def __load_config(self, config_fname):
        config_file = open(config_fname)
        return json.loads(config_file.read())

    def __load_service(self):
        app = Flask("cartiv")

        @app.route("/", methods=['GET'])
        def hello_world():
            return "<p>Hello, World!</p>"

        @app.route("/about", methods = ['GET'])
        def about():
            return "<h1>This is the about page!</h1>"

        @app.route("/login", methods = ['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                new_db = dbmanager.db('users.db')
                row = new_db.get_user_by_id(username, new_db.hash_password(password))
                if row is None:
                    flash('Login failed!', category = 'error')
                else:
                    flash('Login successfully!', category = 'success')

            return render_template("login.html", boolean=True)



        @app.route("/register", methods = ['POST', 'GET'])
        def register():
            if request.method == 'GET':
                return render_template("register.html", boolean = True)
            elif request.method == 'POST':
                firstName = request.form.get('firstName')
                lastName = request.form.get('lastName')
                username = request.form.get('username')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                email = request.form.get('email')

                if ((firstName is None) or (lastName is None) or (username is None) or (password1 is None) or (email is None)):
                    flash('Data cannot be empty.', category= 'error')
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
                    #print(new_db.get_users())
                    flash('Account created successfully!', category = 'success')

            return render_template("register.html", boolean = True)




        # Add "Update shopping list" post request endpoint here

        return app

    def run(self):
        self.app.run()