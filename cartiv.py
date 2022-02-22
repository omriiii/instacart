
import json
import dbmanager
from flask import Flask, request, render_template, flash

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
            data = request.form
            return render_template("login.html", boolean = True)

        @app.route("/register", methods = ['POST', 'GET'])
        def register():
            data = request.form
            '''
            return render_template("register.html", boolean = True)
            '''
            if request.method == 'POST':
                firstName = request.form.get('firstName')
                lastName = request.form.get('lastName')
                username = request.form.get('username')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                email = request.form.get('email')

                if len(firstName) < 2:
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
                    flash('Account created successfully!', category = 'success')

            return render_template("register.html", boolean = True)

        """
        @app.route("/login", methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                return "<h1>Login Page</h1>"
            elif request.method == 'POST':
                login_data = request.form  # a multidict containing POST data
            return
        """

        # Add "Update shopping list" post request endpoint here

        return app

    def run(self):
        self.app.run()