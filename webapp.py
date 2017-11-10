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
        mostPerformed = get_most_performed(year)
        return render_template('popularitydisplay.html', options=get_year_options(), year=year, mostPerformed=mostPerformed[0], performances=mostPerformed[1])
    return render_template('popularity.html', options=get_year_options())

def get_most_performed(year):
    """Returns a list of the name and number of performances of the show that was performed most in the specified year."""
    with open('broadway.json') as broadway_data:
        weeks = json.load(broadway_data)
    #create a dictionary of shows and number of performances in the specified year
    performances = {}
    for w in weeks:
        if str(w["Date"]["Year"]) == year:
            if w["Show"]["Name"] in performances:
                performances[w["Show"]["Name"]] = performances[w["Show"]["Name"]] + w["Statistics"]["Performances"]
            else:
                performances[w["Show"]["Name"]] = w["Statistics"]["Performances"]
    #search the dictionary for the show with the most performances
    name = ""
    perfs = 0
    num = 0
    for s,p in performances.items():
        if p == perfs:
            num += 1
        if p > perfs:
            name = s
            perfs = p
            num = 1
    return [name, str(num)]

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
