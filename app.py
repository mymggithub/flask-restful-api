from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
import mysql.connector
import json

mydb = mysql.connector.connect(
	host="127.0.0.1", 
	user="root", 
	passwd="pass123word",
	database="yiiadv"
)

mycursor = mydb.cursor(dictionary=True, buffered=True)

app = Flask(__name__)
api = Api(app)

class IsOnline(Resource):
	def get(self):
		try:
			mycursor.execute("SELECT * FROM twitter")
			myresult = mycursor.fetchall()
		except Exception as e:
			return {'status':False}

		return {'status':True}

class TwitterHomeApi(Resource):
	def get(self):
		mycursor.execute("SELECT * FROM twitter")
		myresult = mycursor.fetchall()
		json_data=[] 
		for i,x in enumerate(myresult):
			json_data.append([i,x])
		return {'twitter':json_data}

	def post(self):
		args = request.json
		proj_id = t_username = desc = ""
		following = followers = 0
		if "proj_id" in args:
			proj_id = int(args["proj_id"])
		if "t_username" in args:
			t_username = str(args["t_username"])
		if "following" in args:
			following = int(args["following"])
		if "followers" in args:
			followers = int(args["followers"])
		if "desc" in args:
			desc = str(args["desc"])
		if "bday" in args:
			bday = str(args["bday"])

		mycursor.execute("SELECT * FROM `twitter` WHERE t_username = '{0}'".format(t_username))
		myresult = mycursor.fetchall()
		if len(myresult) == 0:
			sql = "INSERT INTO twitter (`twit_id`, `proj_id`, `t_username`, `following`, `followers`, `description`, `last_tweet_id`, `last_popular_tweet_id`, `bday`) VALUES (NULL, %s, %s, %s, %s, %s, '0', '0', %s)"
			mycursor.execute(sql, (proj_id, t_username, following, followers, desc, bday))
			mydb.commit()
			return make_response(jsonify({"success":bool(mycursor.rowcount)}), 201)
			
		return make_response(jsonify({"success":"Exists"}), 200)


class FindId(Resource):
	def get(self, t_username):
		mycursor.execute("SELECT * FROM `twitter` WHERE t_username = '{0}'".format(t_username))
		myresult = mycursor.fetchall()
		return {'result':myresult}

api.add_resource(TwitterHomeApi, '/')
api.add_resource(IsOnline, '/online/')
api.add_resource(FindId, '/find_user/<string:t_username>')

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')

# {"proj_id":"1", "account":"hi", "following":"100", "followers":"5"}
# https://gist.github.com/Jan-Zeiseweis/d45a7206590d1f3577a51dae9517275e