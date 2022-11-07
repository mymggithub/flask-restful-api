#!/usr/bin/python3
import os, sys, copy, json, logging
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import mysql.connector

if not os.path.exists("log"):
	os.mkdir('log');

logging.basicConfig(filename="log/default.log");
log = logging.getLogger('werkzeug');
log.setLevel(logging.ERROR);

DBconfig = {
	"host":"mysql-db", 
	"user":"root", 
	"passwd":"pass123word",
	"database":"yiiadv"
};

app = Flask(__name__);
cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app);

def output_json(data, code):
	if 'callback' in request.args:
		return make_response('{funcname}({data})'.format( funcname=request.args.get('callback'), data=json.dumps(data) ), code);
	return make_response(jsonify(data), code);

class IsOnline(Resource):
	def get(self):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT * FROM twitter;""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchone();
			mydb.close();
			return output_json({ "success":True, "status":True }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "status":False, "error":e, "msg":"Error loading database" }, 200);

class Info(Resource):
	def get(self):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT COUNT(`twit_id`) AS `total`, (COUNT(`twit_id`)-COUNT(CASE WHEN `cached` = 1 AND `cached` THEN 1 END) - COUNT(CASE WHEN `skip` = 1 AND `skip` THEN 1 END)) AS `missing`, COUNT(CASE WHEN `cached` = 1 AND `cached` THEN 1 END) AS `num_cached`, COUNT(CASE WHEN `skip` = 1 AND `skip` THEN 1 END) AS `num_skipped` FROM `twitter`;""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchone();
			mydb.close();
			return output_json({ "status":True, 'data':myresult }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "status":False, "error":e, "msg":"Error loading database" }, 400);

class UpdateWillWont(Resource):
	def get(self):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""UPDATE `twitter` SET `will_f` = (CASE WHEN (`following`-`followers`) > 0 THEN FLOOR((`following`-`followers`)*(100/`following`)) ELSE 0 END), `wont_f` = (CASE WHEN (`followers`-`following`) > 0 THEN FLOOR((`followers`-`following`)*(100/`followers`)) ELSE 0 END);""";
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
			return output_json({ "success":True, "status":True }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "status":False, "error":e, "msg":"Error loading database" }, 400);

class TwitterHomeApi(Resource):
	def get(self):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			limit = "";
			if 'start' in request.args and 'offset' in request.args:
				limit = f"""LIMIT {int(request.args.get('offset'))} OFFSET {int(request.args.get('start'))}""";
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT * FROM `twitter` {limit};""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchall();
			mydb.close();
			return output_json({ "success":True, 'data':myresult }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "status":False, "error":e, "msg":"Error loading database" }, 400);

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
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);

		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query += f"""SELECT * FROM `twitter` WHERE `t_username` LIKE '{t_username}';""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchall();
			if len(myresult) == 0:
				sql_query_tmp = f"INSERT INTO twitter (`twit_id`, `proj_id`, `t_username`, `following`, `followers`, `description`, `last_tweet_id`, `last_popular_tweet_id`, `bday`, `will_f`, `wont_f`, `cached`, `skip`) VALUES (NULL, %(proj_id)s, %(t_username)s, %(following)s, %(followers)s, %(description)s, '0', '0', %(bday)s, 0, 0, 0, 0);";
				sql_query += sql_query_tmp+";";
				mycursor.execute(sql_query_tmp, {"proj_id": proj_id, "t_username": t_username, "following": following, "followers": followers, "description": desc, "bday": bday});
				mydb.commit();
				mydb.close();
				return output_json({ "success":bool(mycursor.rowcount), "msg":"Created" }, 201);
			return output_json({ "success":False, "msg":"Exists" }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with mysql" }, 400);


class ReDownload(Resource):
	def post(self):
		args = request.json;
		proj_id = 1;
		t_username = [];
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);

			if "t_usernames" in args and type(args["t_usernames"])  == list:
				t_usernames = [str(x) for x in args["t_usernames"]];

		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);
		sql_query = "";
		try:
			if len(t_usernames):
				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				for username in t_usernames:
					sql_query_tmp = f"""UPDATE `twitter` SET `cached` = 0, `skip` = 0 WHERE `t_username` LIKE '{username}';""";
					sql_query += sql_query_tmp;
					mycursor.execute(sql_query_tmp);
				sql_query_tmp = f"""UPDATE `settings` SET `settings_value` = 1 WHERE `settings_name` = 'restart_bio';""";
				sql_query += sql_query_tmp;
				mycursor.execute(sql_query_tmp);
				mydb.commit();
				mydb.close();
				if bool(mycursor.rowcount):
					return output_json({ "success":True, "msg":"Redownload Activated" }, 201);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class ReScan(Resource):
	def post(self):
		args = request.json;
		proj_id = 1;
		t_username = [];
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);

			if "t_usernames" in args and type(args["t_usernames"])  == list:
				t_usernames = [str(x) for x in args["t_usernames"]];

		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);
		sql_query = "";
		try:
			if len(t_usernames):
				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				for username in t_usernames:
					sql_query_tmp = f"""UPDATE `twitter` SET `updated` = 0 WHERE `t_username` LIKE '{username}';""";
					sql_query += sql_query_tmp;
					mycursor.execute(sql_query_tmp);
				mydb.commit();
				mydb.close();
				if bool(mycursor.rowcount):
					return output_json({ "success":True, "msg":"Rescan Activated" }, 201);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class FindUsername(Resource):
	def get(self, t_username):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT * FROM `twitter` WHERE t_username LIKE '{t_username}';""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchall();
			mydb.close();
			if bool(mycursor.rowcount):
				return output_json({ "success":True, "msg":"Found" , 'data':myresult }, 200);
			return output_json({ "success":False, "msg":"No data found" }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class DeleteUsername(Resource):
	def get(self, t_username):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""DELETE FROM `twitter` WHERE t_username LIKE '{t_username}';""";
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
			if bool(mycursor.rowcount):
				return output_json({ "success":True, "msg":"Deleted" }, 201);
			return output_json({ "success":False, "msg":"Already Deleted" }, 200);#Already Deleted | Failed to delete
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class DeleteUsernames(Resource):
	def post(self):
		args = request.json;
		proj_id = 1;
		t_username = [];
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);

			if "t_usernames" in args and type(args["t_usernames"])  == list:
				t_usernames = [str(x) for x in args["t_usernames"]];

		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);

		sql_query = "";
		try:
			if len(t_usernames):
				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				sql_query += "DELETE FROM `twitter` WHERE `t_username` IN";
				sql_query += "({})".format(", ".join(["'{}'".format(x) for x in t_usernames]));
				mycursor.execute(sql_query);
				mydb.commit();
				mydb.close();
				if bool(mycursor.rowcount):
					return output_json({ "success":True, "msg":"Deleted" }, 201);
				return output_json({ "success":False, "msg":"Already Deleted" }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class UpdateUsername(Resource):
	def post(self, t_username):
		args = request.json;
		try:
			desc = bday = "";
			following = followers = 0;
			sql_add = [];
			if "following" in args:
				sql_add.append("`following` = {}".format(int(args["following"]))); 
			if "followers" in args:
				sql_add.append("`followers` = {}".format(int(args["followers"]))); 
			if "desc" in args:
				desc = str(args["desc"]).encode("ascii", "ignore").decode();
				sql_add.append(f"`description` = '%(description)s'"%{"description": desc}); 
			if "bday" in args:
				sql_add.append("`bday` = '{}'".format(str(args["bday"])));
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);


		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = "UPDATE `twitter` SET {} WHERE `t_username` LIKE '{}';".format(", ".join(sql_add), t_username);
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
			if bool(mycursor.rowcount):
				return output_json({ "success":True, "msg":"Updated" }, 201);
			return output_json({ "success":False, "msg":"Nothing to update" }, 200);#Nothing to updated | Failed to update
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);



class Settings(Resource):
	def get(self):
		sql_query = "";
		try:
			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT * FROM `settings`""";
			mycursor.execute(sql_query);
			myresult = mycursor.fetchall();
			mydb.close();
			json_data={};
			for i,x in enumerate(myresult):
				json_data[x["settings_name"]] = x["settings_value"];
			if bool(mycursor.rowcount):
				return output_json({ "success":True, 'data':json_data }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);


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
					sql_query = f"""UPDATE `settings` SET `settings_value` = 1 WHERE `settings_name` = 'paused';""";
					msg = "Paused";
				else: 
					sql_query = f"""UPDATE `settings` SET `settings_value` = 0 WHERE `settings_name` = 'paused';""";
					msg = "Unpaused";
			mycursor.execute(sql_query);
			mydb.commit();
			mydb.close();
			if bool(mycursor.rowcount):
				return output_json({ "success":True, "msg":msg }, 201);
			return output_json({ "success":False, "msg":"Nothing to update" }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);

class AddFollowers(Resource):
	def post(self):
		args = request.json;
		proj_id = 1;
		t_username = [];
		try:
			if "proj_id" in args:
				proj_id = int(args["proj_id"]);

			if "t_usernames" in args and type(args["t_usernames"])  == list:
				t_usernames = [str(x) for x in args["t_usernames"]];

		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(args);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":e, "msg":"Error with the vars" }, 400);

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
				if bool(mycursor.rowcount):
					return output_json({ "success":True, "msg":"Created" }, 201);
				return output_json({ "success":False, "msg":"Exists" }, 200);
		except Exception as e:
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			logging.info(sql_query);
			logging.error(e);
			logging.debug(f"-----{self.__class__.__name__}::{sys._getframe().f_code.co_name}()-----");
			return output_json({ "success":False, "error":str(e), "sql":sql_query, "msg":"Error with mysql" }, 400);
			# return Response(str(e), status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)

api.add_resource(TwitterHomeApi, '/');
api.add_resource(IsOnline, '/online/');
api.add_resource(Info, '/info/');
api.add_resource(FindUsername, '/find_user/<string:t_username>');
api.add_resource(DeleteUsername, '/del_user/<string:t_username>');
api.add_resource(DeleteUsernames, '/del_users/');
api.add_resource(UpdateUsername, '/update_user/<string:t_username>');
api.add_resource(Settings, '/settings/');
api.add_resource(AddFollowers, '/add_followers/');
api.add_resource(UpdateWillWont, '/updateWillWont/');
api.add_resource(ReDownload, '/redownload/');
api.add_resource(ReScan, '/rescan/');


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0');