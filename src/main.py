# by Richi Rod AKA @richionline / falken20

import os
from flask import Flask, render_template, url_for
from dotenv import load_dotenv, find_dotenv

from src.logger import Log, console
from src.weather import get_weather_data

console.rule("Cercedilla Weather Web")

# Looking for .env file for environment vars
load_dotenv(find_dotenv())

app = Flask(__name__, template_folder="../templates", static_folder="../static")
# Set this var to True to be able to make any web change and take the changes with refresh
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
@app.route("/home")
def home():
    Log.info(f"Access to home page")
    url_for('static', filename='main.css')

    get_weather_data()

    return render_template("main.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


if __name__ == "__main__":
    app.run(debug=True)
