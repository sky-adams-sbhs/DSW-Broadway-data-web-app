from flask import Flask, request, Markup, render_template, flash

import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('about.html')

def is_localhost():
    """ Determines if app is running on localhost or not
    Adapted from: https://stackoverflow.com/questions/17077863/how-to-see-if-a-flask-app-is-being-run-on-localhost
    """
    root_url = request.url_root
    developer_url = 'http://127.0.0.1:5000/'
    return root_url == developer_url


if __name__ == '__main__':
    app.run(debug=True) # change to False when running in production
