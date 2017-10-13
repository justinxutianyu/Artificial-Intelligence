import config
import cPickle
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash

application = Flask(__name__)
application.config.from_object(config)

def loadTraining():
    return #cPickle.load(open(application.config["TRAIN"]))

@application.before_request
def before_request():
    g.db = loadTraining()

@application.teardown_request
def teardown_request(exception):
    return

@application.route("/")
def home():
    return render_template(
        "index.html"
    )

@application.route("/set_model", methods=["POST"])
def set_model():
    for thing in request.form:
        print(thing)
    return render_template(
        "index.html",
    )

if __name__ == "__main__":
    application.run()
