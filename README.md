OpenIC
======

An Open Information Center.
This project repo for the PA Consultancy Raspberry Pi competition.

This project includes a webserver using flask for viewing and downloading information.
It works best when set up in a reverse proxy with something like nginx.

It comes with a web interface using a modified Bootstrap for adding infomation, viewing information and managing how and where the infomation is sent to.
OpenIC also comes with an API so that you could write a mobile app to communicate with it.

Groups
======

OpenIC allows you to put different roles of people in different groups. 
For example, you may have a Staff group and a Visitors group.
The admin, or designated user can then decide to push infomation to those groups via the web interface and API.
