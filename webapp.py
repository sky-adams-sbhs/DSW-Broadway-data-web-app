from flask import Flask, request, Markup, render_template, flash

import os
import json

app = Flask(__name__)

@app.route('/')
def render_about():
    return render_template('about.html')

@app.route('/popularity')
def render_popularity():
    if 'year' in request.args:
        year = request.args['year']
        return render_template('popularitydisplay.html', options=get_year_options(), year=year)
    return render_template('popularity.html', options=get_year_options())

def get_year_options():
    """Returns the html code for a drop down menu.  Each option is a year for which there is complete data (1990 and 2016 are missing data)."""
    with open('broadway.json') as broadway_data:
        weeks = json.load(broadway_data)
    years = []
    options = ""
    for w in weeks:
        year = w["Date"]["Year"]
        if (year not in years) and not (year == 1990 or year == 2016):
            years.append(year)
            options += Markup("<option value=\"" + str(year) + "\">" + str(year) + "</option>")
    return options
 
def is_localhost():
    """ Determines if app is running on localhost or not
    Adapted from: https://stackoverflow.com/questions/17077863/how-to-see-if-a-flask-app-is-being-run-on-localhost
    """
    root_url = request.url_root
    developer_url = 'http://127.0.0.1:5000/'
    return root_url == developer_url


if __name__ == '__main__':
    app.run(debug=True) # change to False when running in production
