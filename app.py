import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import date, datetime, timezone
import pytz

from helpers import login_required, apology, search, connect

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded. Written by CS50 staff.
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached. Written by CS50 staff.
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies). Written by CS50 staff.
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Define index path, which lists all auditions, chronologically, descending.
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # If method = GET, list the auditions
    if request.method == "GET":
        # Connect to database
        conn = sqlite3.connect("auditionstats.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        user_id = (session["user_id"],)
        c.execute("SELECT * FROM auditions WHERE user_id=? ORDER BY date DESC", user_id)
        r = c.fetchall()

        # Initialize empty lists
        date = []
        title = []
        type_t = []
        role = []
        cd = []
        ca = []
        co = []
        self_tape = []
        cb = []
        booked = []
        notes = []

        # Add items to lists from database
        for i in range(len(r)):
            date.append(r[i]["date"])
            title.append(r[i]["title"])
            type_t.append(r[i]["type"])
            role.append(r[i]["role"])
            cd.append(r[i]["cd"])
            ca.append(r[i]["ca"])
            co.append(r[i]["co"])
            self_tape.append(r[i]["self_tape"])
            cb.append(r[i]["cb"])
            booked.append(r[i]["booked"])
            notes.append(r[i]["notes"])

        # Close database
        conn.close()

        return render_template("index.html", **locals())

    # If method = POST, the row is being edited.
    else:
        #Figure out which row is being edited
        rowId = int(request.form.get("rowId"))
        
        # Connect to database, get all auditions
        conn = sqlite3.connect("auditionstats.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        user_id = (session["user_id"],)
        c.execute("SELECT * FROM auditions WHERE user_id=? ORDER BY date DESC", user_id)
        r = c.fetchall()

        # Initialize  variables for edit page
        year = int(r[rowId]["date"][:4])
        month = int(r[rowId]["date"][5:7])
        day = int(r[rowId]["date"][8:])
        title = r[rowId]["title"]
        type_t = r[rowId]["type"]
        role = r[rowId]["role"]
        co_old = r[rowId]["co"]
        cd_old = r[rowId]["cd"]
        ca_old = r[rowId]["ca"]
        cb = r[rowId]["cb"]
        booked = r[rowId]["booked"]
        self_tape = r[rowId]["self_tape"]
        notes = r[rowId]["notes"]
        row_id =r[rowId]["id"]

        # Populate casting lists
        co = []
        cd = []
        ca = []
        for i in range(len(r)):
            if r[i]["co"] not in co and r[i]["co"] != None and r[i]["co"] != co_old:
                co.append(r[i]["co"])
            if r[i]["cd"] not in cd and r[i]["cd"] != None and r[i]["cd"] != cd_old:    
                cd.append(r[i]["cd"])
            if r[i]["ca"] not in ca and r[i]["ca"] != None and r[i]["ca"] != ca_old:
                ca.append(r[i]["ca"])

        # Populate types and roles.  
        types = ["Theatre", "TV", "Film", "Commercial", "Voiceover"]
        roles = ["Co Star", "Guest Star", "Recurring", "Series Regular", "Supporting", "Lead", "N/A"]

        # Sort casting lists alphabetically
        co = sorted(co)
        cd = sorted(cd)
        ca = sorted(ca)

        # Close database
        conn.close()

        return render_template("edit.html", **locals())

# This route allows user to add auditions to their database.
@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "GET":
        # Initialize casting lists
        co = []
        cd = []
        ca = []

        # Connect to database
        conn = sqlite3.connect("auditionstats.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        user_id = (session["user_id"],)
        c.execute("SELECT * FROM auditions WHERE user_id=?", user_id)
        r = c.fetchall()

        # Populate casting lists but don't add duplicates
        for i in range(len(r)):
            if r[i]["co"] not in co and r[i]["co"] != None:
                co.append(r[i]["co"])
            if r[i]["cd"] not in cd and r[i]["cd"] != None:    
                cd.append(r[i]["cd"])
            if r[i]["ca"] not in ca and r[i]["ca"] != None:
                ca.append(r[i]["ca"])

        # Sort casting lists alphabetically
        co = sorted(co)
        cd = sorted(cd)
        ca = sorted(ca)

        # Close database
        conn.close()

        return render_template("new.html", **locals())

    # If request method = POST, save data to database    
    else:
        # Save date
        month = request.form.get("month")
        day = request.form.get("day")
        year = request.form.get("year")

        # Return apology if they do not choose a full date
        if month == "Month..." or day == "Day...":
            return apology("Must choose a date", 403)

        # Check to make sure the date is valid
        month = int(month)
        day = int(day)
        if month == 4 or 6 or 9 or 11:
            if day > 30:
                return apology("Invalid date", 403)
        if month == 2 and day > 28:
            return apology("Invalid date", 403)

        # Start saving data in variables
        user_id = session["user_id"]
        date = f"{year}-{month:02d}-{day:02d}"
        title = request.form.get("title")
        type_t = request.form.get("type")
        role = request.form.get("role")

        # Make sure user chose a role and a type
        if role == "Choose..." or type_t == "Choose...":
            return apology("Must choose a role and a type", 403)

        # Save the rest of the data
        cd = request.form.get("cd")
        if cd == "Enter new:" or cd == "Choose...":
            cd = request.form.get("cd_new")
            if cd == "":
                cd = None
        ca = request.form.get("ca")
        if ca == "Enter new:" or ca == "Choose...":
            ca = request.form.get("ca_new")
            if ca == "":
                ca = None
        co = request.form.get("co")
        if co == "Enter new:" or co == "Choose...":
            co = request.form.get("co_new")
            if co == "":
                co = None
        self_tape = request.form.get("self_tape")
        if self_tape:
            self_tape = "Self Tape"
        cb = request.form.get("cb")
        if cb:
            cb = "Called Back"
        booked = request.form.get("booked")
        if booked:
            booked = "Booked"
        notes = request.form.get("notes")
        
        # Save all of the values in a tuple
        values = (user_id, date, title, type_t, role, cd, ca, co, self_tape, cb, booked, notes)
        
        # Save the data in the database
        conn = sqlite3.connect("auditionstats.db")
        c = conn.cursor()
        c.execute("""
        INSERT INTO auditions (user_id, date, title, type, role, cd, ca, co, self_tape, cb, booked, notes) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", values)
        conn.commit()
        conn.close()
        return redirect("/")

# This route just re-routes the user home
@app.route("/auditions")
@login_required
def auditions():
    return redirect("/")

# This route allows the user to filter their auditions based on whatever criteria they desire
@app.route("/filter", methods=["GET", "POST"])
@login_required
def filter():
    if request.method == "GET":
        # Initialize casting lists
        co = []
        cd = []
        ca = []

        # Connect to database
        conn = sqlite3.connect("auditionstats.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        user_id = (session["user_id"],)
        c.execute("SELECT * FROM auditions WHERE user_id=?", user_id)
        r = c.fetchall()

        # Populate casting lists, skipping duplicates
        for i in range(len(r)):
            if r[i]["co"] not in co and r[i]["co"] != None:
                co.append(r[i]["co"])
            if r[i]["cd"] not in cd and r[i]["cd"] != None:    
                cd.append(r[i]["cd"])
            if r[i]["ca"] not in ca and r[i]["ca"] != None:
                ca.append(r[i]["ca"])

        # Sort casting lists alphabetically
        co = sorted(co)
        cd = sorted(cd)
        ca = sorted(ca)

        # Close database
        conn.close()
        return render_template("filter.html", **locals())

    # If request method = POST, filter out rows of auditions based on search criteria    
    else: 
        # Connect to database
        r = connect(session["user_id"])

        # Save search criteria in variables
        year = request.form.get("year")
        month = request.form.get("month")
        day = request.form.get("day")
        title = request.form.get("title")
        type_t = request.form.get("type")
        role = request.form.get("role")
        co = request.form.get("co")
        cd = request.form.get("cd")
        ca = request.form.get("ca")

        # Change these variables from bools to strings (important later)
        cb = request.form.get("cb")
        if cb:
            cb = "Called Back"
        booked = request.form.get("booked")
        if booked:
            booked = "Booked"
        self_tape = request.form.get("self_tape")
        if self_tape:
            self_tape = "Self Tape"

        # Delete rows of auditions if they don't match search criteria for date
        if year != "Year...":
            for i in range(len(r) - 1, -1, -1):
                if r[i][2][:4] != year:
                    del r[i]
        
        if month and month != "Month...":
            month = int(month)
            month = f"{month:02d}"
            for i in range(len(r) - 1, -1, -1):
                if r[i][2][5:7] != month:
                    del r[i]

        if day and day != "Day...":
            day = int(day)
            day = f"{day:02d}"
            for i in range(len(r) - 1, -1, -1):
                if r[i][2][8:] != day:
                    del r[i]

        # Delete rows that do not contain the criteria.
        r = search(title, 3, r)
        r = search(type_t, 4, r)
        r = search(role, 5, r)
        r = search(cd, 6, r)
        r = search(ca, 7, r)
        r = search(co, 8, r)
        r = search(self_tape, 9, r)
        r = search(cb, 10, r)
        r = search(booked, 11, r)

        # Initialize empty lists to show results
        date = []
        title = []
        type_t = []
        role = []
        cd = []
        ca = []
        co = []
        self_tape = []
        cb = []
        booked = []
        notes = []

        # Populate lists
        for i in range(len(r)):
            date.append(r[i][2])
            title.append(r[i][3])
            type_t.append(r[i][4])
            role.append(r[i][5])
            cd.append(r[i][6])
            ca.append(r[i][7])
            co.append(r[i][8])
            self_tape.append(r[i][9])
            cb.append(r[i][10])
            booked.append(r[i][11])
            notes.append(r[i][12])

        return render_template("filtered.html", **locals())

# This route lists a sum for each audition category, organized by year
@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    # List audition sums for each year in the database
    if request.method == "GET":
        # Connect to database
        r = connect(session["user_id"])

        # Initialize empty list of years, and a list of keys
        years = []
        keys = ["Year",
        "All", 
        "Theatre", 
        "TV", 
        "Film", 
        "Commercial",
        "Voiceover",
        "Co Star",
        "Guest Star",
        "Recurring",
        "Series Regular",
        "Supporting",
        "Lead",
        "N/A",
        "Self Tape",
        "Called Back",
        "Booked"]

        # Populate years list
        for i in range(len(r)):
            year = r[i][2][:4]
            if year not in years:
                years.append(year)
        
        # Create empty dictionaries for each year
        d = [{} for x in range(len(years))]

        # Set years value to year
        for i in range(len(years)):
            d[i][keys[0]] = years[i]

        # Set rest of values to zero
        for i in range(len(years)):
            for j in range(1, len(keys)):
                d[i][keys[j]] = 0
        
        # Count auditions
        for i in range(len(years)):        
            for j in range(len(r)):
                if years[i] == r[j][2][:4]:
                    d[i][keys[1]] += 1
        
        # Count the rest of the categories
        for i in range(len(d)):
            for j in range(len(r)):
                for k in range(2, len(keys)):
                    if d[i][keys[0]] == r[j][2][:4]:
                        if keys[k] in r[j]:
                            d[i][keys[k]] += 1
        
        return render_template("stats.html", **locals())

    # If a year is clicked:    
    else:
        # Get that year
        year = request.form.get("bookingId")

        # Connect to database
        r = connect(session["user_id"])

        # Initialize keys
        keys = ["All",
        "Theatre",
        "TV",
        "Film",
        "Commercial",
        "Voiceover"]

        # Initialize dictionary titles
        ds = ["Total", 
        "Booked", 
        "Percentage"]

        # Create empty dictionaries for each of the titles
        d = [{} for x in range(len(ds))]

        # Set dict values to zero
        for i in range(len(ds)):
            for j in range(len(keys)):
                d[i][keys[j]] = 0

        # Find total auditions & auditions for each category (filling d[0])
        for i in range(len(r)):
            if year == r[i][2][:4]:
                d[0][keys[0]] += 1
                for j in range(1, len(keys)):
                    if keys[j] in r[i]:
                        d[0][keys[j]] += 1

        # Find auditions booked (filling d[1])
        for i in range(len(r)):
            if year == r[i][2][:4] and r[i][11] == "Booked":
                d[1][keys[0]] += 1
                for j in range(1, len(keys)):
                    if keys[j] in r[i]:
                        d[1][keys[j]] += 1

        # Calculate percentage (filling d[2])
        for i in range(len(keys)):
            if d[0][keys[i]] != 0:
                d[2][keys[i]] = float(d[1][keys[i]]/d[0][keys[i]])
                d[2][keys[i]] = "{:.0%}".format(d[2][keys[i]])
            else:
                d[2][keys[i]] = "N/A"
        
        return render_template("percentage.html", **locals())

# The route called if the user POSTS an edit to one of the entries
@app.route("/edit", methods=["POST"])
def edit():
    # Get data from the form
    row_id = request.form.get("rowId")
    month = int(request.form.get("month"))
    day = int(request.form.get("day"))
    year = request.form.get("year")

    # Check for a valid date
    if month in (4, 6, 9, 11):
        if day > 30:
            return apology("Invalid date", 403)

    if month == 2 and day > 28:
        return apology("Invalid date", 403)

    # Continue to save data from the form
    date = f"{year}-{month:02d}-{day:02d}"
    title = request.form.get("title")
    type_t = request.form.get("type")
    role = request.form.get("role")

    # Make sure casting entries are valid
    cd = request.form.get("cd")
    if cd == "Enter new:":
        cd = request.form.get("cd_new")
        if cd == "":
            cd = None
    ca = request.form.get("ca")
    if ca == "Enter new:":
        ca = request.form.get("ca_new")
        if ca == "":
            ca = None
    co = request.form.get("co")
    if co == "Enter new:":
        co = request.form.get("co_new")
        if co == "":
            co = None

    # Save final values        
    self_tape = request.form.get("self_tape")
    if self_tape:
        self_tape = "Self Tape"
    cb = request.form.get("cb")
    if cb:
        cb = "Called Back"
    booked = request.form.get("booked")
    if booked:
        booked = "Booked"
    notes = request.form.get("notes")

    # Save values in a tuple
    values = (date, title, type_t, role, cd, ca, co, self_tape, cb, booked, notes, row_id)
    
    # Update data in database
    conn = sqlite3.connect("auditionstats.db")
    c = conn.cursor()
    c.execute("UPDATE auditions SET date=?, title=?, type=?, role=?, cd=?, ca=?, co=?, self_tape=?, cb=?, booked=?, notes=? WHERE id=?", values)
    conn.commit()
    conn.close()
    return redirect("/")

# This route allows user to delete a row from their database
@app.route("/delete", methods=["POST"])
def delete():
    # Find which row the user wants to delete
    delete_id = int(request.form.get("deleteId"))

    # Connect to database 
    conn = sqlite3.connect("auditionstats.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    user_id = (session["user_id"],)
    c.execute("SELECT * FROM auditions WHERE user_id=? ORDER BY date DESC", user_id)
    r = c.fetchall()

    # Convert delete id to id of the actual audition log row
    id = (r[delete_id]["id"],)

    # Delete that row from databse
    c.execute("DELETE FROM auditions WHERE id=?", id)
    conn.commit()
    conn.close()

    return redirect("/")

# Allows user to register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Save username, password and confirmation entries
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check to make sure that everything was entered correctly
        if not username:
            return apology("must provide username", 403)
        elif not password or not confirmation:
            return apology("must provide password & password confirmation", 403)
        else:
            if password != confirmation:
                return apology("passwords must match", 403)
            
            # If everything checks out, save the data to the users table
            else:
                pw_hash = generate_password_hash(password)
                conn = sqlite3.connect("auditionstats.db")
                c = conn.cursor()
                values = (username, pw_hash)
                c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", values)
                conn.commit()
                conn.close()
                return redirect("/")

# This route allows a user to login. Most of this code was written by staff at CS50.
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)

        conn = sqlite3.connect("auditionstats.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        username2 = (username,)
        c.execute("SELECT * FROM users WHERE username=?", username2)
        r = c.fetchall()

        if not r or not check_password_hash(r[0]["hash"], request.form.get("password")):
            conn.close()
            return apology("invalid username and/or password", 403)

        session["user_id"] = r[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

# Allows user to log out.  Also written by staff at CS50.
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# This handles errors if they arise. Written by CS50 staff.
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors. Written by CS50 staff.
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

