from datetime import timedelta
import md5
import random
from uuid import uuid4
from flask import Flask, request, redirect, render_template, session
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from itsdangerous import URLSafeTimedSerializer
import sqlite3 as sql

import captcha

DATABASE = 'openic.db' #Database name
 
app = Flask(__name__)
app.debug = True
app.secret_key = "OpenIC_H|>;@\%x0PG'rvse>BHJuvxDXV[XciN(YC97-*Cdd[j~b/E!HKXu.i8k+YmcuygHKOxS6)bcno<<sm`ITZu%^xR;QXX9/{R#V^n^.{;'C$<[S=wGDf1]q?m50jRk!."
login_serializer = URLSafeTimedSerializer(app.secret_key)
login_manager = LoginManager()

def get_db():
	db = getattr(g, '_database', None) #Is the database already existing
	if db is None: #If it doesn't exist create it
		db = g._database = sql.connect(DATABASE)
	return db #return the database
@app.teardown_appcontext
def close_connection(exception): #Called at the end of each request
	try:
		db = getattr(g, '_database', None)
		if db is not None:
			db.close() #Close the database
	except NameError:
		pass
class User(UserMixin):
	def __init__(self, userid, password):
		self.id = userid
		self.password = password
		self.db = sql.connect(DATABASE)
		self.cur = self.db.cursor()
 
	def get_auth_token(self):
		data = [str(self.id), self.password]
		return login_serializer.dumps(data)

	def __del__(self):
		self.db.close()
 
	@staticmethod
	def get(userid):
		db = sql.connect(DATABASE)
		cur = db.cursor()
		for user in list(cur.execute("SELECT USERNAME, PASSWORD FROM Users")):
			if user[0] == userid:
				db.close()
				return User(user[0], user[1])
		db.close()
		return None
 
def hash_pass(password):
	salted_password = password + app.secret_key
	return md5.new(salted_password).hexdigest()
 
@login_manager.user_loader
def load_user(userid):
	return User.get(userid)
 
@login_manager.token_loader
def load_token(token):
	max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
	#Decrypt the Security Token, data = [username, hashpass]
	data = login_serializer.loads(token, max_age=max_age)
	#Find the User
	user = User.get(data[0])
	#Check Password and return user or None
	if user and data[1] == user.password:
		return user
	return None
 
@app.route("/logout/")
def logout_page():
	logout_user()
	return redirect("/")
 
@app.route("/login/", methods=["GET", "POST"])
def login_page():
	if request.method == "POST":
		user = User.get(request.form['username'])
		if user and hash_pass(request.form['password']) == user.password:
			login_user(user, remember="remember" in request.form)
			return redirect(request.args.get("next") or "/")
	return render_template("login.html")
 
@app.route("/signup/", methods=["GET", "POST"])
def signup_page():
	db = sql.connect("registrants.db")
	cur = db.cursor()
	if request.method == "POST":
		word = ""
		for registrant in list(cur.execute("SELECT ID, CAPTCHA FROM Registrants")):
#			print session['rid'], registrant
			if session['rid'] == registrant[0]:
				word = registrant[1].lower()
				cur.execute('DELETE FROM "Registrants" WHERE ID = ?;', (session['rid'], ))
				db.commit()
				session.clear()
		if word == request.form["captcha_input"] and request.form['password_confirm'] == request.form['password'] and request.form['password'] != "":
			userdb = sql.connect(DATABASE)
			usercur = userdb.cursor()
			if not ((request.form["username"],) in list(usercur.execute("SELECT USERNAME FROM Users")) or request.form["username"].isspace() or len(request.form["username"]) < 4):
				usercur.execute("INSERT INTO Users VALUES(NULL, ?, ?, 0, ?, ?)", (request.form["username"], request.form["name"], hash_pass(request.form['password']), None)) #Create user
			userdb.commit()
			userdb.close()
	html = render_template("signup.html")
	dictionary_f = open("/usr/share/dict/words")
	dictionary = dictionary_f.read().split("\n")
	dictionary_f.close()
	word = random.choice(dictionary)
	uid = str(uuid4())
	session['rid'] = uid
	cur.execute('INSERT INTO "Registrants" VALUES(?, ?);', (uid, word))
	cap = captcha.captcha(word)
	strhtml = str(html).replace("<p>%captcha%</p>", cap) #cap
	db.commit()
	db.close()
	return strhtml

@app.route("/")
def index_page():
	user_id = (current_user.get_id() or "")
	return render_template("index.html", user_id = user_id)

#@app.route("/restricted/")
#@login_required

if __name__ == "__main__":
	#print hash_pass("OpenIC")
	app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)
	login_manager.login_view = "/login/"
	#Setup the login manager.
	login_manager.setup_app(app)	
	#Run the flask Development Server
	app.run()
