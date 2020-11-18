# audition-mathematician
Audition Log Flask Web App for Actors

I designed a web application (based partly on a web app developed in Harvard's CS50 class) that allows actors to log their auditions online and produce statistics about their auditions from that data.  There is also a feature that allows actors to search their audition databases.  They also have the option to edit entries or delete them. The app uses Flask and relies heavily on sqlite 3.

As an actor myself, we get very little information about what's working and what's not. The only real data we have pertains to auditions: How many are we getting? How many are we booking? Etc. We're famously bad at keeping track of what casting offices we've been in for, and which associates work at what offices, etc. This app allows a person to keep track of every audition they go on and produce stats for each audition year, giving the actor a more concrete view of their progress in a career that can frequently feel murky and intangible.

PAGES:

Auditions:
    This presents a table with every audition that the actor has been on, ordered chronologically, descending. Every audition has a date, title, type, role, casting office, casting director, casting associate, called-back, booked, self-tape field. Each entry has a button that allows the user to edit the entry, or delete the entry.

New:
    This allows the user to enter a new audition into their database.  Some fields are required.  There's use of javascript to add functionality around disabling/enabling fields depending on what the user has selected.

Filter:
    This page allows the user to search their auditions using as many or as few fields as they desire.  Only auditions matching all the fields they've selected will appear.

Stats:
    This page filters the data by year and provides totals for each category of audition, allowing the user to see how their audition stats have changed from year to year.  An actor can also click on a year to see a breakdown of how many jobs they booked by category, and what their "booking percentage" is for each.

INSTRUCTIONS:  Once you create a virtual python environment, use command "flask run" to launch the project.
