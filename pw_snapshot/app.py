#!/usr/bin/python

import os
import time
import random
import mysql.connector
from playwright.sync_api import sync_playwright
import logging
import requests
import io
from PIL import Image

if not os.path.exists("log"):
	os.mkdir('log');
if not os.path.exists("pics"):
	os.mkdir('pics');
if not os.path.exists("pics/shots"):
	os.mkdir('pics/shots');
if not os.path.exists("pics/shots"):
	os.mkdir('pics/shots');
if not os.path.exists("pics/pfp"):
	os.mkdir('pics/pfp');

logging.basicConfig(filename="log/default.log");
logging.getLogger().setLevel(logging.DEBUG);
logging.getLogger().setLevel(logging.INFO);

DBconfig = {
	"host":"mysql_db", 
	"user":"root", 
	"passwd":"pass123word",
	"database":"yiiadv"
};

KEEP_ALIVE = False;


def img_down(link, filename):
	response  = requests.get(link).content 
	image_file = io.BytesIO(response)
	image  = Image.open(image_file).convert('RGB')
	split_tup = os.path.splitext(link);
	msg = "pics/pfp/{}{}".format(filename, str(split_tup[1]));
	logging.info(msg);
	print(msg, flush=True);
	image.save("pics/pfp/{}{}".format(filename, str(split_tup[1])) , "JPEG");
	msg = "Downladed PFP";
	logging.info(msg);
	print(msg, flush=True);

try:
	time.sleep(5)
	mydb = mysql.connector.connect(**DBconfig);
	mycursor = mydb.cursor(dictionary=True);
	mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
	myresult = mycursor.fetchone();
	mydb.close();
	cont_loop = (myresult["settings_value"] == 1);
	while cont_loop:
		msg = "Bio_snapshot: On";
		logging.info(msg);
		print(msg, flush=True);
		time.sleep(1)
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True);
		mycursor.execute("SELECT `t_username` FROM `twitter`");
		all_user_results = mycursor.fetchall();
		mydb.close();
		if len(all_user_results):
			for i,x in enumerate(all_user_results):
				u = x["t_username"];
				if not os.path.exists("pics/shots/{}.png".format(u)):
					with sync_playwright() as p:
						browser = p.chromium.launch()
						page = browser.new_page()
						msg = "{}/{} - Opening https://twitter.com/{}".format(i+1,len(all_user_results),u);
						logging.info(msg);
						print(msg, flush=True);
						page.goto("https://twitter.com/{}".format(u));
						page.wait_for_selector('img');
						page.screenshot(path="pics/shots/{}.png".format(u))
						img_elem = page.query_selector('[href="/{}/photo"] img'.format(u));
						if img_elem is not None:
							img_down(img_elem.get_attribute('src'), u);
						else:
							msg = "PFP Missing";
							logging.info(msg);
							print(msg, flush=True);
						browser.close()

					msg = "{} Saved".format(u);
					logging.info(msg);
					print(msg, flush=True);
					wait_time = random.randint(15, 65);
					msg = "Waiting: {} Sec".format(wait_time);
					logging.info(msg);
					print(msg, flush=True);
					time.sleep(wait_time);

				else:
					msg = "{}/{} - Skipping: {}".format(i+1,len(all_user_results),u);
					logging.info(msg);
					print(msg, flush=True);

				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True);
				mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
				myresult = mycursor.fetchone();
				mydb.close();
				cont_loop = (myresult["settings_value"] == 1);
				if not cont_loop:
					msg = "Quiting";
					logging.info(msg);
					print(msg, flush=True);
					break;
		else:
			break;

	msg = "Done";
	logging.info(msg);
	print(msg, flush=True);

except Exception as e:
	logging.debug("----------");
	logging.error(e);
	logging.debug("----------");
	print(e, flush=True);
	while KEEP_ALIVE:
		print("Debug mode", flush=True);
		time.sleep(60);