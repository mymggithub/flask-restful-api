#!/usr/bin/python3
import os, sys, copy, json, logging
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
import mysql.connector

if not os.path.exists("log"):
	os.mkdir('log');

logging.basicConfig(filename="log/default.log");
log = logging.getLogger('werkzeug');
# log.setLevel(logging.ERROR);

DBconfig = {
	"host":"mysql-db", 
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
			return make_response(jsonify({ "success":False, "status":False, "error":e, "msg":"Error loading database" }), 200);

		return make_response(jsonify({ "success":True, "status":True }), 200);

class Info(Resource):
	def get(self):
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			mycursor.execute("SELECT COUNT(`twit_id`) AS `total`, (COUNT(`twit_id`)-COUNT(CASE WHEN `cached` = 1 AND `cached` THEN 1 END) - COUNT(CASE WHEN `skip` = 1 AND `skip` THEN 1 END)) AS `missing`, COUNT(CASE WHEN `cached` = 1 AND `cached` THEN 1 END) AS `num_cached`, COUNT(CASE WHEN `skip` = 1 AND `skip` THEN 1 END) AS `num_skipped` FROM `twitter`;");
			myresult = mycursor.fetchone();
			mydb.close();
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "status":False, "error":e, "msg":"Error loading database" }), 200);

		if request.args == {}:
			return make_response(jsonify({ "status":True, 'data':myresult }), 200);
		else:
			return make_response('{funcname}({data})'.format( funcname=request.args.get('callback'), data=json.dumps({ "success":True, 'data':myresult }) ), 200);

class UpdateWillWont(Resource):
	def get(self):
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"UPDATE `twitter` SET `will_f` = (CASE WHEN (`following`-`followers`) > 0 THEN FLOOR((`following`-`followers`)*(100/`following`)) ELSE 0 END), `wont_f` = (CASE WHEN (`followers`-`following`) > 0 THEN FLOOR((`followers`-`following`)*(100/`followers`)) ELSE 0 END);";
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "status":False, "error":e, "msg":"Error loading database" }), 200);

		return make_response(jsonify({ "success":True, "status":True }), 200);

class TwitterHomeApi(Resource):
	def get(self):
		mydb = mysql.connector.connect(**DBconfig);
		limit = "";
		if 'start' in request.args and 'offset' in request.args:
			limit = "LIMIT {} OFFSET {}".format(int(request.args.get('offset')), int(request.args.get('start')));
		mycursor = mydb.cursor(dictionary=True, buffered=True);
		sql = "SELECT * FROM `twitter` {};".format(limit);
		mycursor.execute(sql);
		myresult = mycursor.fetchall();
		mydb.close();
		if 'callback' not in request.args:
			return make_response(jsonify({ "success":True, 'data':myresult }), 200);
		else:
			return make_response('{funcname}({data})'.format( funcname=request.args.get('callback'), data=json.dumps({ "success":True, 'data':myresult }) ), 200);
		


	def post(self):
		args = request.json;
		proj_id = t_username = desc = bday = "";
		following = followers = 0;
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);
			if "t_username" in args:
				t_username = str(args["t_username"]);
				if t_username.strip() == "":
					return make_response(jsonify({ "success":False, "msg":"Blank Usernamse" }), 400);
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
				sql_query = f"INSERT INTO twitter (`twit_id`, `proj_id`, `t_username`, `following`, `followers`, `description`, `last_tweet_id`, `last_popular_tweet_id`, `bday`, `will_f`, `wont_f`, `cached`, `skip`) VALUES (NULL, %(proj_id)s, %(t_username)s, %(following)s, %(followers)s, %(description)s, '0', '0', %(bday)s, 0, 0, 0, 0)";
				mycursor.execute(sql_query, {"proj_id": proj_id, "t_username": t_username, "following": following, "followers": followers, "description": desc, "bday": bday});
				mydb.commit();
				mydb.close();
				return make_response(jsonify({ "success":bool(mycursor.rowcount), "msg":"Created" }), 201);
			return make_response(jsonify({ "success":False, "msg":"Exists" }), 200);
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
			sql_query = f"UPDATE `twitter` SET "+(", ".join(sql_add))+" WHERE `t_username` LIKE '{}'; UPDATE `twitter` SET `will_f` = (CASE WHEN (`following`-`followers`) > 0 THEN FLOOR((`following`-`followers`)*(100/`following`)) ELSE 0 END), `wont_f` = (CASE WHEN (`followers`-`following`) > 0 THEN FLOOR((`followers`-`following`)*(100/`followers`)) ELSE 0 END);".format(t_username);
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



class Settings(Resource):
	def get(self):
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True, buffered=True);
		sql_query = "SELECT * FROM `settings`";
		mycursor.execute(sql_query);
		myresult = mycursor.fetchall();
		mydb.close();
		json_data={};
		for i,x in enumerate(myresult):
			json_data[x["settings_name"]] = x["settings_value"];
		if len(myresult) > 0:
			return make_response(jsonify({ "success":True, 'data':json_data }), 200);


	def post(self):
		args = request.json;
		pause = 0;
		sql_query = "";
		msg = "Updated";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			if "pause" in args:
				if int(args["pause"]) == 1:
					sql_query = f"UPDATE `settings` SET `settings_value` = 1 WHERE `settings_name` = 'paused'";
					msg = "Paused";
				else: 
					sql_query = f"UPDATE `settings` SET `settings_value` = 0 WHERE `settings_name` = 'paused'";
					msg = "Unpaused";
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(sql_query);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
		if bool(mycursor.rowcount):
			return make_response(jsonify({ "success":True, "msg":msg }), 201);
		return make_response(jsonify({ "success":False, "msg":"Nothing to update" }), 200);

class AddFollowers(Resource):
	def post(self):
		args = request.json;
		proj_id = 2;
		t_username = [];
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);

			if "t_usernames" in args and type(args["t_usernames"])  == list:
				t_usernames = [str(x) for x in args["t_usernames"]];

		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(args);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "error":e, "msg":"Error with the vars" }), 400);

		sql_query = "";
		try:
			if len(t_usernames):
				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				sql_query += "INSERT IGNORE INTO `twitter` (`twit_id`, `proj_id`, `t_username`, `following`, `followers`, `description`, `last_tweet_id`, `last_popular_tweet_id`, `bday`, `will_f`, `wont_f`, `cached`, `skip`) VALUES";
				sql_query += str(", ".join(["(NULL, "+str(proj_id)+", '"+str(x)+"', 0, 0, '', '0', '0', '', 0, 0, 0, 0)" for x in t_usernames]));
				mycursor.execute(sql_query);
				mydb.commit();
				mydb.close();
				return make_response(jsonify({ "success":bool(mycursor.rowcount), "msg":"Created" }), 201);
			return make_response(jsonify({ "success":False, "msg":"Exists" }), 200);
		except Exception as e:
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			logging.info(sql_query);
			logging.error(e);
			logging.debug("-----{}::{}()-----".format(self.__class__.__name__,  sys._getframe().f_code.co_name));
			return make_response(jsonify({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }), 400);
			# return Response(str(e), status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)

api.add_resource(TwitterHomeApi, '/');
api.add_resource(IsOnline, '/online/');
api.add_resource(Info, '/info/');
api.add_resource(FindUsername, '/find_user/<string:t_username>');
api.add_resource(DeleteUsername, '/del_user/<string:t_username>');
api.add_resource(UpdateUsername, '/update_user/<string:t_username>');
api.add_resource(Settings, '/settings/');
api.add_resource(AddFollowers, '/add_followers/');


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0');