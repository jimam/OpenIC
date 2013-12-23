 #!/usr/bin/env python

#Flask imports
from flask import Flask
from flask import Response
from flask import request

#Other imports
import json

app = Flask(__name__) #Setup flask

@app.route("/")
def testView():
	ret = dict(zip(request.args.keys(), request.args.values())) #Create a dictionary of keys and values
	
	#resp = Response(response=repr(ret),
	#				status=200,
	#				mimetype="text/html")

	resp = Response(response=json.dumps(ret),
					status=200,
					mimetype="application/json") #Correct json response
	return resp

if __name__ == '__main__':
	app.debug = True #Comment when actual
	app.run("localhost",7777) #Host locally on port 7777
