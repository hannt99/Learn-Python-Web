from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result/<count>')
def user(count):
    return render_template('result.html', count=count)
