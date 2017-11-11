from flask import Flask, request, Markup, render_template, flash

import os
import json

app = Flask(__name__)

@app.route('/')
def render_about():
    return render_template('about.html')

@app.route('/popularity')
def render_popularity():
    with open('broadway.json') as broadway_data:
        weeks = json.load(broadway_data)
    if 'year' in request.args:
        year = request.args['year']
        mostPerformed = get_most_performed(weeks, year)
        mostAttended = get_most_attended(weeks, year)
        return render_template('popularitydisplay.html', options=get_year_options(weeks), year=year, mostPerformed=mostPerformed[0], 
                               performances=mostPerformed[1], tickets=mostAttended[1], mostAttended=mostAttended[0])
    return render_template('popularity.html', options=get_year_options(weeks))

def get_show_and_max_val(data, year, statsKey):
    """Returns a list of the name(s) of the shows(s) with the max total value for the year of the specified statsKey"""
    #create a dictionary of shows and totals of the specified statsKey for the specified year
    shows = {}
    for w in data:
        if str(w["Date"]["Year"]) == year:
            if w["Show"]["Name"] in shows:
                shows[w["Show"]["Name"]] = shows[w["Show"]["Name"]] + w["Statistics"][statsKey]
            else:
                shows[w["Show"]["Name"]] = w["Statistics"][statsKey]
    #search the dictionary for the show with the highest value
    names = []
    val = 0
    for s,v in shows.items():
        if v == val:
            names.append(s)
        if v > val:
            names = [s]
            val = v
    return [names,val]

def get_most_attended(data, year):
    """Returns a list of the name(s) and number of tickets sold of the show(s) that sold the most tickets the specified year."""
    result = get_show_and_max_val(data, year, "Attendance")
    names = result[0]
    tics = result[1]
    #format the names of the most attended shows
    shows = ""
    if len(names) > 2:
        for i in range(0,len(names)-1):
            shows = shows + names[i] + ", "
        shows = shows + "and " + names[-1]
    elif len(names) == 2:
        shows = names[0] + " and " + names[1]
    else:
        shows = names[0]
    return [shows, str(tics)]

def get_most_performed(data, year):
    """Returns a list of the name(s) and number of performances of the show(s) that was performed most in the specified year."""
    result = get_show_and_max_val(data, year, "Performances")
    names = result[0]
    perfs = result[1]
    #format the names of the most performed shows
    shows = ""
    if len(names) > 2:
        for i in range(0,len(names)-1):
            shows = shows + names[i] + ", "
        shows = shows + "and " + names[-1] + " were"
    elif len(names) == 2:
        shows = names[0] + " and " + names[1] + " were"
    else:
        shows = names[0] + " was"
    return [shows, str(perfs)]

def get_year_options(weeks):
    """Returns the html code for a drop down menu.  Each option is a year for which there is complete data (1990 and 2016 are missing data)."""
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
