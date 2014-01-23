#!/usr/bin/env python

#Flask imports
from flask import Flask
from flask import Response
from flask import request
from flask import g

#Other imports
import json
import sqlite3 as sql
import datetime
import hashlib
import uuid

DATABASE = 'openic.db' #Database name
PERMISSION_NAMES = {"post_all":0, \
                    "delete_others":1, \
                    "add_user":2, \
                    "change_passwords":3, \
                    "set_perms":4, \
                    "post_group":5, \
                    "set_groups":6, \
					"view_all": 7} #Permission bits

app = Flask(__name__) #Setup flask

def get_db():
	db = getattr(g, '_database', None) #Is the database already existing
	if db is None: #If it doesn't exist create it
		db = g._database = sql.connect(DATABASE)
	return db #return the database

@app.teardown_appcontext
def close_connection(exception): #Called at the end of each request
	db = getattr(g, '_database', None)
	if db is not None:
		db.close() #Close the database

@app.route("/addcomment_all")
def addcomment_all(): #Add a comment
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
#	if auth_user(query): #Authorise the user
#		return returnJSON([query["auth_username"], "didn't type in their correct password"])
	if 1:
#	if get_perms(query["auth_username"], "post_all"): #If the user has posting permissions...
		cur.execute("INSERT INTO Comments VALUES(NULL, ?, ?, ?, 'all')", (query["auth_username"], query["comment"], str(datetime.datetime.now()).split(".")[0])) #Add the comment
		get_db().commit()
		return returnJSON("Comment %s was posted to all users" %(query["comment"]))
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to post to everyone"])

@app.route("/addcomment_group")
def addcomment_group(): #Add a comment
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query): #Authorise the user
		return returnJSON([query["auth_username"], "didn't type in their correct password"])
	if (get_perms(query["auth_username"], "post_all")) or \
	   (get_perms(query["auth_username"], "post_group") and cur.execute("SELECT Users.username,Groups.groupname FROM Users,Groups,Users_Groups WHERE Users_Groups.userID=Users.ID AND Users_Groups.groupID=Groups.ID AND Users.username=?", (query["username"],))): #If the user has posting permissions...
		cur.execute("INSERT INTO Comments VALUES(NULL, ?, ?, ?, ?)", (query["auth_username"], query["comment"], datetime.datetime.now(), query["group_name"])) #Add the comment
		get_db().commit()
		return returnJSON("Comment %s was posted to group %s" %(query["comment"], query["group_name"]))
	else:
		return returnJSON([query["auth_username"], "isn't allowed to post comments"])

@app.route("/get_all_comments")
def get_all_comments(): #Get all comments
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query): #Authorise the user
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	if get_perms(query["auth_user"], "view_all"):
		return returnJSON([query["auth_user"], "isn't allowed to view all the comments"])
	cur = get_db().cursor()
	comments = list(cur.execute("SELECT * FROM Comments")) #Add the comment
	return returnJSON(comments)

@app.route("/get_group_comments")
def get_group_comments(): #Get all comments the user is allowed to see
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query): #Authorise the user
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	cur = get_db().cursor()
	user_groups = list(cur.execute("SELECT Groups.groupname FROM Users,Groups,Users_Groups WHERE Users_Groups.userID=Users.ID AND Users_Groups.groupID=Groups.ID AND Users.username=?", (query["auth_user"],)))
	if ((query["group_name"],) in user_groups) or (("all",) in user_groups):
		comments = list(cur.execute("SELECT * FROM Comments WHERE group_name = ?", (query["group_name"],)))
		return returnJSON(comments)
	else:
		return returnJSON([query["auth_user"], "isn't in group", query["group_name"]])


@app.route("/add_group")
def add_group(): #Add a user to a group
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query): #Authorise the user
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	if get_perms(query["auth_user"], "set_groups"): #If the user has add group permissions)
		if len(list(cur.execute("SELECT * FROM Groups WHERE groupname = ?", (query["group"],)))) == 0:
			cur.execute("INSERT INTO Groups VALUES(?, ?)", (len(list(cur.execute("SELECT * FROM Groups")))+1, query["group"]))
		get_db().commit()
		cur.execute("INSERT INTO Users_Groups VALUES(NULL,?,?);"(list(cur.execute("SELECT ID FROM Users WHERE username = ?", (query["username"],)))[0], list(cur.execute("SELECT ID FROM Groups WHERE groupname = ?", (query["group"],)))[0]))
		get_db().commit()
		return returnJSON("Complete")
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to add users to groups"])


@app.route("/adduser")
def adduser(): #Add a user
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query):
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	if get_perms(query["auth_user"], "add_user"): #If the user has add user permissions
		salt = uuid.uuid4().hex #Create the salt
		password = hashlib.sha512(query["password"] + salt).hexdigest() #Generate the hashed password
		if len(list(cur.execute('SELECT * FROM Users WHERE username = ?', (query["username"],)))) == 0: #If we dont have any users with that username
			cur.execute("INSERT INTO Users VALUES(NULL, ?, 16, ?, ?, ?)", (query["username"], password, salt, None)) #Create user
		else:
			return returnJSON(["Fail", "User with that name already created"])
		get_db().commit()
		return returnJSON(["Complete", salt]) #User might want their salt
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to create user accounts"])

@app.route("/elevate_permissions")
def elevate_permissions():
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query): #Authorise the user
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	if get_perms(query["auth_user"], "set_perms"):
		cur.execute("UPDATE Users SET permissions = ? WHERE username=?;", (query["new_perm_level"], query["username"])) #Elevate permissions to level
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to elevate other users permissions"])
	get_db().commit()
	return returnJSON(["Complete"])

def auth_user(query): #Authorises the user with a username and password
	return False
"""	username = query["auth_user"]
	password = query["auth_password"]
	cur = get_db().cursor()
	try:
		auth_password = hashlib.sha512(password + list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][4]).hexdigest() #Hashed password
		return auth_password != list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][3] #Is it the same as the one we have stored?
	except IndexError:
		raise AssertionError("User doesn't exist")"""

def get_perms(username, perm):
	return False
"""	cur = get_db().cursor()
	try:
		return bool(list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][2] >> PERMISSION_NAMES[perm]) #Get permission int then bitwise the permission number
	except IndexError:
		raise AssertionError("User doesn't exist")"""

def returnJSON(ret):
   	try:
		resp = Response(response=json.dumps(ret),
						status=200,
						mimetype="application/json") #Correct json response
	except TypeError: #Not seriable by JSON
		print "Return is not JSON seriable:\n\n"+repr(ret)
		resp = Response(response="Return is not JSON seriable:\n\nContent:\t"+repr(ret),
						status=200,
						mimetype="text/plain") #Return in plaintext instead
	return resp

if __name__ == '__main__':
	app.debug = True #Comment when actual
	app.run("localhost",7777) #Host locally on port 7777
