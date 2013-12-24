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

DATABASE = 'openic.db'
PERMISSION_NAMES = {"post":0, "delete_others":1, "create_user":2, "change_passwords":3, "set_perms":4}

app = Flask(__name__) #Setup flask

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sql.connect(DATABASE)
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.route("/addcomment")
def addcomment():
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	userID = query["userID"]
	cur = get_db().cursor()
	if get_perms("post"):
		cur.execute("INSERT INTO Comments VALUES(NULL, ?, ?, ?)", (userID, query["comment"], datetime.datetime.now()))
		get_db().commit()
		return returnJSON("Comment %s was posted to all users" %(query["comment"]))
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to elevate other users permissions"])

@app.route("/adduser")
def adduser():
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if get_perms("add_user"):
		salt = uuid.uuid4().hex
		password = hashlib.sha512(query["password"] + salt).hexdigest()
		if len(list(cur.execute('SELECT * FROM Users WHERE username = ?', (query["username"],)))) == 0:
			cur.execute("INSERT INTO Users VALUES(NULL, ?, 16, ?, ?)", (query["username"], password, salt))
		else:
			return returnJSON(["Fail", "User with that name already created"])
		get_db().commit()
		return returnJSON(["Complete", salt])
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to elevate other users permissions"])

@app.route("/elevate_permissions")
def elevate_permissions():
	query = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	cur = get_db().cursor()
	if auth_user(query["auth_user"], query["auth_password"]):	
		return returnJSON([query["auth_user"], "didn't type in their correct password"])
	if get_perms("set_perms"):
		cur.execute("UPDATE Users SET permissions = ? WHERE username=?;", (query["new_perm_level"], query["username"]))
	else:
		return returnJSON([query["auth_user"], "doesn't have permission to elevate other users permissions"])
	get_db().commit()
	return returnJSON(["Complete"])

def auth_user(username, password):
	cur = get_db().cursor()
	auth_password = hashlib.sha512(password + list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][4]).hexdigest()
	return auth_password != list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][3]

def get_perms(username, perm):
	cur = get_db().cursor()
	return list(cur.execute('SELECT * FROM Users WHERE username = ?', (username,)))[0][2] >> PERMISSION_NAMES[perm] == 1:

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
