import os
import md5
import random
import time

from flask import Flask, request, redirect, render_template, session, send_from_directory
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from werkzeug import secure_filename
from itsdangerous import URLSafeTimedSerializer

from datetime import timedelta
import sqlite3 as sql
from uuid import uuid4
import StringIO
import Image

import captcha

DATABASE = 'openic.db' #Database name

UPLOAD_FOLDER = 'Profile_IM'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'])
 
app = Flask(__name__)
app.debug = True
app.secret_key = "OpenIC_H|>;@\%x0PG'rvse>BHJuvxDXV[XciN(YC97-*Cdd[j~b/E!HKXu.i8k+YmcuygHKOxS6)bcno<<sm`ITZu%^xR;QXX9/{R#V^n^.{;'C$<[S=wGDf1]q?m50jRk!."
login_serializer = URLSafeTimedSerializer(app.secret_key)
login_manager = LoginManager()

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

@app.route("/settings/", methods=["GET", "POST"])
@login_required
def settings_page():
	db = sql.connect("openic.db")
	cur = db.cursor()
	filename =  str(list(cur.execute("SELECT ID FROM Users where username = ?", (current_user.get_id(), )))[0][0])
	db.close()
	if request.method == "POST":
		up_file = request.files['upload']
		if up_file and \
				'.' in up_file.filename and \
				up_file.filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
			sync_file = StringIO.StringIO()
			up_file.save(sync_file)
			x = open("static/Profile_IM/"+filename+".png", "wb")
			x.write(sync_file.getvalue())
			x.close()
			im = Image.open("static/Profile_IM/"+filename+".png")
			im = im.resize((148,148))
			im.save("static/Profile_IM/"+filename+".png")
			#print sync_file.getvalue()

		return redirect("/settings/")

	return render_template("settings.html", user_im = filename)
 

@app.route("/signup/", methods=["GET", "POST"])
def signup_page():
	db = sql.connect("registrants.db")
	cur = db.cursor()
	if request.method == "POST":
		word = ""
		for registrant in list(cur.execute("SELECT ID, CAPTCHA FROM Registrants")):
#			print session['rid'], registrant
			try:
				if session['rid'] == registrant[0]:
					word = registrant[1].lower()
					cur.execute('DELETE FROM "Registrants" WHERE ID = ?;', (session['rid'], ))
					db.commit()
					session.clear()
			except KeyError:
				word = None
	 	captcha_right = word == request.form["captcha_input"].lower()
		#print captcha_right, word, request.form["captcha_input"]
		passwords_identical = request.form['password_confirm'] == request.form['password']
		password_not_empty = request.form['password'] != ""
		if captcha_right and passwords_identical and password_not_empty:
			userdb = sql.connect(DATABASE)
			usercur = userdb.cursor()
			user_added = False
			user_existant = (request.form["username"],) in list(usercur.execute("SELECT USERNAME FROM Users"))
			user_space = request.form["username"].isspace()
			user_length = len(request.form["username"]) < 4
			if not ( user_existant or user_space or user_length):
				user_added = True
				usercur.execute("INSERT INTO Users VALUES(NULL, ?, ?, 0, ?)", (request.form["username"], request.form["name"], hash_pass(request.form['password']))) #Create user
				userdb.commit()
				userid = list(cur.execute("SELECT ID FROM Users where username = ?", (request.form["username"], )))[0][0]
			userdb.close()
			if user_added:
				os.system("cp static/Profile_IM/new_user_im.png static/Profile_IM/%s.png"%(userid))
				login_user(User.get(request.form['username']), remember=False)
				return render_template("feedback.html", feedback = ["Success!"], back_location = "/")
		else:
			reason = ""
			if not captcha_right: reason += "Incorrect Captcha\n"
			if not passwords_identical: reason += "Passwords were differant\n"
			if not password_not_empty: reason += "Password box empty\n"
			try:
				if not user_existant: reason += "User already exists\n"
				if not user_space: reason += "User only contains spaces\n"
				if not user_length: reason += "User length too small\n"
			except UnboundLocalError:
				pass
#			print reason
			return render_template("feedback.html", feedback = reason.split("\n"), back_location = "/signup/")
	dictionary_f = open("/usr/share/dict/words")
	dictionary = dictionary_f.read().split("\n")
	dictionary_f.close()
	word = random.choice(dictionary)
	uid = str(uuid4())
	session['rid'] = uid
	cur.execute('INSERT INTO "Registrants" VALUES(?, ?);', (uid, word))
	cap = captcha.captcha(word)
	html = render_template("signup.html")
	strhtml = str(html).replace("<p>%captcha%</p>", word) #cap
	db.commit()
	db.close()
	return strhtml


@app.route("/post/", methods=["GET", "POST"])
@login_required
def post_comment():
	db = sql.connect(DATABASE)
	cur = db.cursor()
	if request.method == "POST":
		group = request.form['group']
		replyid = request.form['replyid']
		comment = request.form['comment']
		userid =  list(cur.execute("SELECT ID FROM Users where username = ?", (current_user.get_id(), )))[0][0]
		cur.execute("INSERT INTO Comments Values(NULL, ?, ?, ?, ?, ?)", (userid, comment, time.time(), group, replyid))
		cur.execute("UPDATE Groups SET lastposted = ? WHERE groupname = ?", (time.time(), group))
		db.commit()
		db.close()
		return redirect("/view/")
	if "comment" in request.args.keys():
		group_id = request.args["comment"]
		group_comments = list(list(cur.execute("SELECT * FROM Comments where ID = ?", (group_id,)))[0])
		group_comments[2] = group_comments[2].split("\n")
		group_comments.extend(list(cur.execute("SELECT username FROM Users where ID = ?", (int(group_comments[1]), )))[0])
		db.close()
		return render_template("post.html", comment=group_comments)
	elif "topic" in request.args.keys():
		db.close()
		return render_template("post.html", group = request.args["topic"])

def commenttree(groupid):
	db = sql.connect(DATABASE)
	cur = db.cursor()
	group_name = list(cur.execute("SELECT groupname FROM Groups where ID = ?", (groupid,)))[0][0]
	group_comments = [list(i) for i in list(cur.execute("SELECT * FROM Comments where group_name = ?", (group_name,)))]
	mv = []
	for group_comment in range(len(group_comments)):
		group_comments[group_comment][2] = group_comments[group_comment][2].split("\n")
		group_comments[group_comment].extend(list(cur.execute("SELECT username FROM Users where ID = ?", (int(group_comments[group_comment][1]), )))[0])

		if  group_comments[group_comment][5] != -1:
			for commentidsearch in range(len(group_comments)):
				if group_comments[commentidsearch][0] == group_comments[group_comment][5]:
					mv.append((group_comment, commentidsearch))
		group_comments[group_comment][5] = []
	for i in reversed(mv):
		group_comments[i[1]][5].append(group_comments[i[0]])
	for i in range(len(mv)):
		del group_comments[mv[i][0]-i]
	db.close()
	return group_comments

@app.route("/view/")
def view_page():
	db = sql.connect(DATABASE)
	cur = db.cursor()
	try:
		userid = list(cur.execute("SELECT ID FROM Users WHERE username = ?", (current_user.get_id(),)))[0][0]
		groupids = list(cur.execute("SELECT groupID FROM Users_Groups WHERE userID = ?", (userid,)))
		if "topic" in request.args.keys():
			if request.args["topic"] in [str(groupid[0]) for groupid in groupids] or request.args["topic"] == "1":
				group_name = list(cur.execute("SELECT groupname FROM Groups where ID = ?", (request.args["topic"])))[0][0]
				group_comments = commenttree(int(request.args["topic"]))
				db.close()
				return render_template("view.html", comments = group_comments,  group=group_name)

		groups = []
		for groupid in groupids:
			groups.append(list(list(cur.execute("SELECT * FROM Groups where ID = ?", (groupid[0],)))[0]))
			#print groups
			groups[-1][1] = groups[-1][1].title()
			groups[-1][2] = time.strftime("%H:%M  %d/%m/%Y", time.localtime(groups[-1][2]))
	except IndexError:
		groups = []
		if "topic" in request.args.keys():
			if request.args["topic"] == "1":
				comments = []
				group_name = list(cur.execute("SELECT groupname FROM Groups where ID = 1"))[0][0]
				group_comments = commenttree("1")
					
				db.close()
				return render_template("view.html", comments = group_comments) 	
	if groups == []:
		groups.append(list(list(cur.execute("SELECT * FROM Groups where ID = ?", (1,)))[0]))
		#print groups
		groups[-1][1] = groups[-1][1].title()
		groups[-1][2] = time.strftime("%H:%M  %d/%m/%Y", time.localtime(groups[-1][2]))
		
	db.close()
	return render_template("view.html", groups = groups)



@app.route("/")
def index_page():
	user_id = (current_user.get_id() or "")
	return render_template("index.html", user_id = user_id)


@app.route('/Profile_IM/<path:filename>')
def base_static(filename):
	return send_from_directory(app.static_folder + '/Profile_IM/', filename)

if __name__ == "__main__":
	#print hash_pass("OpenIC")
	app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=1)
	login_manager.login_view = "/login/"
	#Setup the login manager.
	login_manager.setup_app(app)	
	#Run the flask Development Server
	app.run()
