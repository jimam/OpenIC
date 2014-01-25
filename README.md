OpenIC
======

An Open Information Center.
This project repo for the PA Consultancy Raspberry Pi competition.
OpenIC gives you a way to share infomation between groups of people. Ask questions within your groups and share and discuss infomation.

This project includes a webserver using flask for viewing and downloading information.
It works best when set up in a reverse proxy with something like nginx.

It comes with a web interface using a modified Bootstrap for adding infomation, viewing information and managing how and where the infomation is sent to.
OpenIC also comes with an API so that you could write a mobile app to communicate with it.

Groups
======

OpenIC allows you to put different roles of people in different groups. 
For example, you may have a Staff group and a Visitors group.
The admin, or designated user, can then decide to push infomation or questions to those groups via the web interface and API.

Questions
=========
You can ask a question within your group. The question can then be answered via the web interface or via the API and pushed back to the askers account or mobile device (in the future).
Say I'm on my way home. I can send a question out to a "Family" group (via the API, web app or mobile app), asking if aything needs to be picked up. The question can be answered via the same methods, by any member of the "Family group"

Infomation
==========

Infomation/threads/posts are posted with the web app, API, or a future mobile app. 

API
===

The API is currently not working properly, but it will return JSON data from a call made via http.

Please Note
===========

The mobile device applications haven't been written yet, although the API exists for you to use yourself.
The OpenIC will only currently run under Linux, as it relies on a few Linux specific things.
OpenIC Server will require an internet connection if you want to add users. Otherwise it can be run over a local network, although we don't reccomend this.
