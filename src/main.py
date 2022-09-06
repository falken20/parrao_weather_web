import os
from flask import Flask, render_template, url_for
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Looking for .env file for environment vars
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
print(__name__)

app = Flask(__name__)
# Set this var to True to be able to make any web change and take the changes with refresh
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def home():
    url_for('static', filename='main.css')
    return render_template("main.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


if __name__ == "__main__":
    app.run(debug=True)
