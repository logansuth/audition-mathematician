import os
import requests
import urllib.parse
import sqlite3

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    # Returns a picture with a code if an error occurs. Written by CS50 staff.
    def escape(s):
        # Escapes special characters
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def search(x, num, r):
    # Function created to search the rows for search criteria, deletes if not there
    if x and x != "Choose..." and x != "":
        for i in range(len(r) - 1, -1, -1):
            if r[i][num] != x:
                del r[i]
    return r

def connect(x):
    # Connects to database and delivers all auditions for that user
    conn = sqlite3.connect("auditionstats.db")
    c = conn.cursor()
    user_id = (x,)
    c.execute("SELECT * FROM auditions WHERE user_id=? ORDER BY date DESC", user_id)
    r = c.fetchall()
    conn.close()
    return r


def login_required(f):
    # Used to decorate routes that require a login. Written by CS50 staff.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


