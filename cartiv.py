
import json
import dbmanager
from flask import Flask
from flask import request, render_template

class Cartiv:
    def __init__(self, config_fname):
        self.config = self.__load_config(config_fname)
        self.db = dbmanager.db(self.config["db_fname"])
        self.app = self.__load_service()

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
            #return "<h1>This is the login page!<h1>"
            return render_template("login.html", boolean = True)

        @app.route("/register", methods = ['POST', 'GET'])
        def register():
            data = request.form
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