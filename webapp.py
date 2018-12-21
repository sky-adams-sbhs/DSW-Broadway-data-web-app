from flask import Flask, request, Markup, render_template, flash
from datetime import datetime

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
        mostPerformed = show_most_performed(weeks, year)
        mostAttended = show_most_attended(weeks, year)
        highestGross = show_with_highest_gross(weeks, year)
        mostPerformances = most_popular_theatre(weeks, year, "Performances")
        mostAttendedTheatre = most_popular_theatre(weeks, year, "Attendance")
        return render_template('popularitydisplay.html', options=get_year_options(weeks), year=year, mostPerformed=mostPerformed[0], 
                               performances=mostPerformed[1], tickets=mostAttended[1], mostAttended=mostAttended[0],
                               highestGross=highestGross[0], gross=highestGross[1],
                               theatreMostPerformed=mostPerformances[0], mostPerformances=mostPerformances[1], each_performances=mostPerformances[2],
                               theatreMostAttended=mostAttendedTheatre[0], theatreTickets=mostAttendedTheatre[1], each_attended=mostAttendedTheatre[2])
    return render_template('popularity.html', options=get_year_options(weeks))

@app.route('/databyshow')
def render_databyshow():
    with open('broadway.json') as broadway_data:
        weeks = json.load(broadway_data)
    if 'show' in request.args:
        show = request.args['show']
        runningDates = get_running_dates(weeks, show)
        totals = get_show_totals(weeks, show)
        return render_template('databyshowdisplay.html', options=get_show_options(weeks), show=show, 
            startDate=runningDates[0], endDate = runningDates[1], performances=totals[0], attendance=totals[1],gross=totals[2])
    return render_template('databyshow.html', options=get_show_options(weeks))

@app.route('/spending')
def render_spending():
    with open('broadway.json') as broadway_data:
        weeks = json.load(broadway_data)
    return render_template('spending.html', dataPoints=total_annual_grosses(weeks))
    
def total_annual_grosses(weeks):
    #create a dictionary of year:gross
    years = {}
    for w in weeks:
        year = w["Date"]["Year"]
        if year in years:
            years[year] = years[year] + w["Statistics"]["Gross"]
        else:
            years[year] = w["Statistics"]["Gross"]
    del years[1990]
    del years[2016]
    #create a properly formatted string to use in the jQuery code
    code = "["
    for year, gross in years.items():
        code = code + Markup("{ x: '" + str(year) + "', y: " + str(gross/1000000) + " },")
    code = code[:-1] #remove the last comma
    code = code + "]"
    return code
    
def get_show_totals(data, show):
    perfs = 0
    attendance = 0
    gross = 0
    for w in data:
        if w["Show"]["Name"] == show:
            perfs = perfs + w["Statistics"]["Performances"]
            attendance = attendance + w["Statistics"]["Attendance"]
            gross = gross + w["Statistics"]["Gross"]
    return [format(perfs, ',d'), format(attendance,',d'), format(gross,',d')]
    
def get_running_dates(data, show):
    startDate = datetime.strptime("12/31/2016", '%m/%d/%Y')
    endDate = datetime.strptime("01/01/1990", '%m/%d/%Y')
    for w in data:
        if w["Show"]["Name"] == show:
            date = datetime.strptime(w["Date"]["Full"], '%m/%d/%Y')
            if date < startDate:
                startDate = date
            if date > endDate:
                endDate = date
    return [str(startDate.month) + "/" + str(startDate.year), str(endDate.month) + "/" + str(endDate.year)]
    
def most_popular_theatre(data, year, statsKey):
    result = get_show_and_max_val(data, year, "Theatre", statsKey)
    names = result[0]
    perfs = result[1]
    each = ""
    if len(names) > 1:
        each = " each"
    theatres = list_to_string(names)
    return [theatres, format(perfs,',d'), each]
 
def list_to_string(words):
    """Returns a string in the format 'words[0], words[1], ..., and words[-1]', 'words[0] and words[1]' for lists with only 2 items, and 'words[0]' for lists with only 1 item."""
    result = ""
    if len(words) > 2:
        for i in range(0,len(words)-1):
            result = result + words[i] + ", "
        result = result + "and " + words[-1]
    elif len(words) == 2:
        result = words[0] + " and " + words[1]
    else:
        result = words[0]
    return result
    
def get_show_and_max_val(data, year, showKey, statsKey):
    """Returns a list of the name(s) of the shows(s) with the max total value for the year of the specified statsKey"""
    #create a dictionary of shows/theatres and totals of the specified statsKey for the specified year
    shows = {}
    for w in data:
        if str(w["Date"]["Year"]) == year:
            if w["Show"][showKey] in shows:
                shows[w["Show"][showKey]] = shows[w["Show"][showKey]] + w["Statistics"][statsKey]
            else:
                shows[w["Show"][showKey]] = w["Statistics"][statsKey]
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

def show_with_highest_gross(data, year):
    """Returns a list of the name(s) and total annual gross of the show(s) that grossed the most money in the specified year."""
    """Returns a list of the name(s) and number of tickets sold of the show(s) that sold the most tickets the specified year."""
    result = get_show_and_max_val(data, year, "Name", "Gross")
    names = result[0]
    gross = result[1]
    #format the names of the most attended shows
    shows = list_to_string(names)
    return [shows, format(gross,',d')]
    
def show_most_attended(data, year):
    """Returns a list of the name(s) and number of tickets sold of the show(s) that sold the most tickets the specified year."""
    result = get_show_and_max_val(data, year, "Name", "Attendance")
    names = result[0]
    tics = result[1]
    #format the names of the most attended shows
    shows = list_to_string(names)
    return [shows, format(tics,',d')]

def show_most_performed(data, year):
    """Returns a list of the name(s) and number of performances of the show(s) that was performed most in the specified year."""
    result = get_show_and_max_val(data, year, "Name", "Performances")
    names = result[0]
    perfs = result[1]
    #format the names of the most performed shows
    shows = shows = list_to_string(names)
    if len(names) >= 2:
        shows = shows + " were"
    else:
        shows = shows + " was"
    return [shows, format(perfs,',d')]

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

def get_show_options(weeks):    
    """Returns the html code for a drop down menu.  Each option is a show that has been performed on Broadway."""
    shows = []
    options = ""
    for w in weeks:
        show = w["Show"]["Name"]
        if (show not in shows):
            shows.append(show)
    shows.sort()
    for s in shows:
        options += Markup("<option value=\"" + s + "\">" + s + "</option>")
    return options
 
def is_localhost():
    """ Determines if app is running on localhost or not
    Adapted from: https://stackoverflow.com/questions/17077863/how-to-see-if-a-flask-app-is-being-run-on-localhost
    """
    root_url = request.url_root
    developer_url = 'http://127.0.0.1:5000/'
    return root_url == developer_url


if __name__ == '__main__':
    app.run(debug=False) # change to False when running in production
