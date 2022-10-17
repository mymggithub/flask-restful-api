#!/usr/bin/python

import time
import random
from os.path import exists
import mysql.connector
from playwright.sync_api import sync_playwright

logging.basicConfig(filename="log/default.log");

DBconfig = {
	"host":"mysql_db", 
	"user":"root", 
	"passwd":"pass123word",
	"database":"yiiadv"
};

try:
	time.sleep(5)
	mydb = mysql.connector.connect(**DBconfig);
	mycursor = mydb.cursor(dictionary=True);
	mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
	myresult = mycursor.fetchone();
	mydb.close();
	cont_loop = (myresult["settings_value"] == 1);
	while cont_loop:
		logging.info("Bio_snapshot: On");
		time.sleep(1)
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True);
		mycursor.execute("SELECT `t_username` FROM `twitter`");
		all_user_results = mycursor.fetchall();
		mydb.close();
		for i,x in enumerate(all_user_results):
			u = x["t_username"];
			if not exists("pics/{}.png".format(u)):
				with sync_playwright() as p:
					browser = p.chromium.launch()
					page = browser.new_page()
					logging.info("Opening https://twitter.com/{}".format(u));
					page.goto("https://twitter.com/{}".format(u))
					page.wait_for_selector("img")
					page.screenshot(path="pics/{}.png".format(u))
					browser.close()

				logging.info("{} Saved".format(u));
				wait_time = random.randint(15, 65);
				logging.info("Waiting: {} Sec".format(wait_time));
				time.sleep(wait_time);

			else:
				logging.info("Skipping: {}".format(u));

			mydb = mysql.connector.connect(**DBconfig);
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
			myresult = mycursor.fetchone();
			mydb.close();
			cont_loop = (myresult["settings_value"] == 1);
			if not cont_loop:
				break;

		if i == len(all_user_results)-1:
			cont_loop = False;
		
except Exception as e:
	logging.debug("----------");
	logging.error(e);
	logging.debug("----------");
