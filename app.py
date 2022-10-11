#!/usr/bin/python3
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
import mysql.connector
import json
import logging
import sys

logging.basicConfig(filename="log/default.log");

DBconfig = {
	"host":"127.0.0.1", 
	"user":"root", 
	"passwd":"pass123word",
	"database":"yiiadv"
};

app = Flask(__name__);
api = Api(app);

class IsOnline(Resource):
	def get(self):
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			mycursor.execute("SELECT * FROM twitter");
			myresult = mycursor.fetchone();
			mydb.close();
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "status":False }), 200);

		return make_response(jsonify({ "success":True, "status":True }), 200);

class TwitterHomeApi(Resource):
	def get(self):
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True, buffered=True);
		mycursor.execute("SELECT * FROM twitter");
		myresult = mycursor.fetchall();
		mydb.close();
		json_data=[] ;
		for i,x in enumerate(myresult):
			json_data.append([i,x]);
		return make_response(jsonify({ "success":True, 'data':json_data }), 200);

	def post(self):
		args = request.json;
		try:
			proj_id = t_username = desc = bday = "";
			following = followers = 0;
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);
			if "t_username" in args:
				t_username = str(args["t_username"]);
			if "following" in args:
				following = int(args["following"]);
			if "followers" in args:
				followers = int(args["followers"]);
			if "desc" in args:
				desc = str(args["desc"]).encode("ascii", "ignore");
			if "bday" in args:
				bday = str(args["bday"]);
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(args);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "error":e, "msg":"Error with the vars" }), 400);

		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			mycursor.execute("SELECT * FROM `twitter` WHERE t_username LIKE '{0}'".format(t_username));
			myresult = mycursor.fetchall();
			if len(myresult) == 0:
				sql_query = f"INSERT INTO twitter (`twit_id`, `proj_id`, `t_username`, `following`, `followers`, `description`, `last_tweet_id`, `last_popular_tweet_id`, `bday`) VALUES (NULL, %(proj_id)s, %(t_username)s, %(following)s, %(followers)s, %(description)s, '0', '0', %(bday)s)";
				mycursor.execute(sql_query, {"proj_id": proj_id, "t_username": t_username, "following": following, "followers": followers, "description": desc, "bday": bday});
				mydb.commit();
				return make_response(jsonify({ "success":bool(mycursor.rowcount), "msg":"Created" }), 201);
			mydb.close();
			make_response(jsonify({ "success":False, "msg":"Exists" }), 200);
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(sql_query);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "error":e, "msg":"Error with mysql" }), 400);


class FindUsername(Resource):
	def get(self, t_username):
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True, buffered=True);
		mycursor.execute("SELECT * FROM `twitter` WHERE t_username LIKE '{0}'".format(t_username));
		myresult = mycursor.fetchall();
		mydb.close();
		if bool(mycursor.rowcount):
			return make_response(jsonify({ "success":True, "msg":"Found" , 'data':myresult }), 200);
		return make_response(jsonify({ "success":False, "msg":"No data found" }), 200);

class DeleteUsername(Resource):
	def get(self, t_username):
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True, buffered=True);
		sql_query = "DELETE FROM `twitter` WHERE t_username LIKE '{}'".format(t_username);
		mycursor.execute(sql_query);
		mydb.commit();
		mydb.close();
		if bool(mycursor.rowcount):
			return make_response(jsonify({ "success":True, "msg":"Deleted" }), 201);
		return make_response(jsonify({ "success":False, "msg":"Already Deleted" }), 200);#Already Deleted | Failed to delete

class UpdateUsername(Resource):
	def post(self, t_username):
		args = request.json;
		try:
			desc = bday = "";
			following = followers = 0;
			sql_add = [];
			if "following" in args:
				following = int(args["following"]);
				sql_add.append("`following` = '{}'".format(following)); 
			if "followers" in args:
				followers = int(args["followers"]);
				sql_add.append("`followers` = '{}'".format(followers)); 
			if "desc" in args:
				desc = str(args["desc"]).encode("ascii", "ignore").decode();
				sql_add.append(f"`description` = '%(description)s'"%{"description": desc}); 
			if "bday" in args:
				bday = str(args["bday"]);
				sql_add.append("`bday` = '{}'".format(bday));
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(args);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "error":e, "msg":"Error with the vars" }), 400);


		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"UPDATE `twitter` SET "+(", ".join(sql_add))+" WHERE `t_username` LIKE '{}'".format(t_username);
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(sql_query);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
		if bool(mycursor.rowcount):
			return make_response(jsonify({ "success":True, "msg":"Updated" }), 201);
		return make_response(jsonify({ "success":False, "msg":"Nothing to update" }), 200);#Nothing to updated | Failed to update

api.add_resource(TwitterHomeApi, '/');
api.add_resource(IsOnline, '/online/');
api.add_resource(FindUsername, '/find_user/<string:t_username>');
api.add_resource(DeleteUsername, '/del_user/<string:t_username>');
api.add_resource(UpdateUsername, '/update_user/<string:t_username>');


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0');

# {"proj_id":"1", "account":"hi", "following":"100", "followers":"5"}
# https://gist.github.com/Jan-Zeiseweis/d45a7206590d1f3577a51dae9517275e