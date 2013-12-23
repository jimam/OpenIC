from flask import Flask
from flask import Response
import json

app = Flask(__name__)

@app.route("/")
def testView():
    ret = {"TEST":"Data"}

    resp = Response(response=json.dumps(ret),
                    status=200,
                    mimetype="application/json")

    return resp

if __name__ == '__main__':
	app.debug = True
	app.run("localhost",80)
