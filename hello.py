#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'



# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    
    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT * FROM temperature")
    else:
        curs.execute("select strftime('%%Y-%%m-%%dT%%H:00:00.000', timestamp), avg(value) from temperature where timestamp>datetime('now', '-%s hours') group by strftime('%%Y-%%m-%%dT%%H:00:00.000', timestamp)" % interval)

    rows=curs.fetchall()

	
    conn.close()

    return rows


# convert rows from database into a javascript table
def create_table(rows):
    chart_table=""

    for row in rows[:-1]:
        rowstr="['{0}', {1}],\n".format(str(row[0]),str(row[1]))
        chart_table+=rowstr

    row=rows[-1]
    rowstr="['{0}', {1}]\n".format(str(row[0]),str(row[1]))
    chart_table+=rowstr

    return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Time', 'Temperature'],
%s
        ]);

        var options = {
          title: 'Temperature'
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""

    print chart_code % (table)




# print the div that contains the graph
def show_graph():
    print "<h2>Temperature Chart</h2>"
    print '<div id="chart_div" style="width: 900px; height: 500px;"></div>'



# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    curs.execute("SELECT * FROM temperature order by timestamp desc limit 1")
    rowcurr=curs.fetchone()
    rowstrcurr="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowcurr[0]),str(rowcurr[1]))

    curs.execute("SELECT timestamp,max(value) FROM temperature WHERE timestamp>datetime('now','-%s hour')" % option)
    rowmax=curs.fetchone()
    rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT timestamp,min(value) FROM temperature WHERE timestamp>datetime('now','-%s hour')" % option)
    rowmin=curs.fetchone()
    rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(value) FROM temperature WHERE timestamp>datetime('now','-%s hour') " % option)
  
    rowavg=curs.fetchone()


    print "<hr>"

    print "<h2>Current temperature&nbsp</h2>"
    print rowstrcurr
    print "<h2>Minumum temperature&nbsp</h2>"
    print rowstrmin
    print "<h2>Maximum temperature</h2>"
    print rowstrmax
    print "<h2>Average temperature</h2>"
    print "%.3f" % rowavg+"C"

    print "<hr>"

    print "<h2>In the last hour:</h2>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    rows=curs.execute("SELECT * FROM temperature WHERE timestamp>datetime('now','-1 hour')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1}C</td></tr>".format(str(row[0]),str(row[1]))
        print rowstr
    print "</table>"

    print "<hr>"

    conn.close()

def print_minmax_settings():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("SELECT * FROM configuration limit 1")
    row=curs.fetchone()

    mintemp=row[0]
    maxtemp=row[1]

    print """<form action="/cgi-bin/hello.py" method="POST">"""
    print "Temperature alert<br>"
    print """Minimum temperature: <input type="text" name="mintemp" value="%f"/><br>""" %mintemp
    print """Maximum temperature:<input type="text" name="maxtemp"  value="%f"/><br>""" %maxtemp
    print """<input type="submit" value="Save" /><br>"""
    print "</form>"

    

    conn.close()



def print_time_selector(option):
	
    print """<form action="/cgi-bin/hello.py" method="POST">
        Show the temperature logs for  
        <select name="timeinterval">"""


    if option is not None:

	if option == "4":
            print "<option value=\"4\" selected=\"selected\">the last 4 hours</option>"
        else:
            print "<option value=\"4\">the last 4 hours</option>"

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
        else:
            print "<option value=\"6\">the last 6 hours</option>"

	if option == "8":
            print "<option value=\"8\" selected=\"selected\">the last 8 hours</option>"
        else:
            print "<option value=\"8\">the last 8 hours</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>"
        else:
            print "<option value=\"12\">the last 12 hours</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

    else:
        print """
		<option value="4">the last 4 hours</option>
		<option value="6">the last 6 hours</option>
		<option value="8">the last 6 hours</option>
           	<option value="12">the last 12 hours</option>
            	<option value="24" selected="selected">the last 24 hours</option>"""

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else: 
        return None


def submit_form():
    form=cgi.FieldStorage()
    if "mintemp" in form and "maxtemp" in form:
	conn=sqlite3.connect(dbname)
	conn.execute("DELETE from configuration")
        conn.execute("INSERT INTO configuration (mintemp) values(%f)" %float(form["mintemp"].value))
	conn.execute("UPDATE configuration SET maxtemp = %f WHERE mintemp is not null" %float(form["maxtemp"].value))
	conn.commit()
     	conn.close()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None


# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    option=submit_form()

    if option is None:
        option = str(24)

    # get data from the database
    records=get_data(option)

    # print the HTTP header
    printHTTPheader()

    if len(records) != 0:
        # convert the data into a table
        table=create_table(records)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    printHTMLHead("Raspberry Pi Temperature Logger", table)

    # print the page body
    print "<body>"
    print "<h1>Raspberry Pi Temperature Logger</h1>"
    print "<hr>"
    print_time_selector(option)
    print_minmax_settings()
    show_graph()
    show_stats(option)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()



