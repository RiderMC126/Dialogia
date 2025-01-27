from flask import Flask, render_template, request, redirect, url_for, session
from config import *


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/images/'


@app.route('/')
def index():
    title = 'Dialogia'
    return render_template("index.html", title=title)


if __name__ == '__main__':
    app.run(debug=True)
