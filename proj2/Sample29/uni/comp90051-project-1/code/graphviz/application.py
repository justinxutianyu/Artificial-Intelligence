import config
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash

application = Flask(__name__)
application.config.from_object(config)

def connect_db():
    #Establish a connection to the DB specified in config
    return sqlite3.connect(application.config["DATABASE"])

def init_db():
    #Populates the database using a pre-defined schema
    with closing(connect_db()) as db:
        with application.open_resource("schema.sql", mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@application.before_request
def before_request():
    #g.db = connect_db()
    return None

@application.teardown_request
def teardown_request(exception):
    #db = getattr(g, "db", None)
    #if db is not None:
    #    db.close()
    return None

@application.route("/")
def home():
    return render_template(
        "index.html"
    )

@application.route("/number", methods=["POST"])
def number():
    return render_template(
        "numbers.html",
        number=request.form["number"]
    )

if __name__ == "__main__":
    application.run()
