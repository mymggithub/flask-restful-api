#!/usr/bin/python

import io
import os
import time
import random
import mysql.connector
from playwright.sync_api import sync_playwright
import logging
import requests
from lxml import html
from PIL import Image
required_folders = {
	"log":"log",
	"pics":"pics",
	"shots":"pics/shots",
	"pfp":"pics/pfp",
	"cache":"cache"
}
for dir_var in required_folders:
	if not os.path.exists(required_folders[dir_var]):
		os.mkdir(required_folders[dir_var]);

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

def hide_elem_JSxpath(pg, current_xpath):
	pg.evaluate("""() =>  document.evaluate(`{}`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.display = "none" """.format(current_xpath));

def show_msg(msg):
	logging.info(msg);
	print(msg, flush=True);

def img_down(link, filename):
	response  = requests.get(link).content 
	image_file = io.BytesIO(response)
	image  = Image.open(image_file).convert('RGB')
	split_tup = os.path.splitext(link);
	show_msg( "{}/{}{}".format(required_folders["pfp"], filename, str(split_tup[1])) );
	image.save("{}/{}{}".format(required_folders["pfp"], filename, str(split_tup[1])) , "JPEG");
	show_msg("Downladed PFP");

try:
	time.sleep(5)
	mydb = mysql.connector.connect(**DBconfig);
	mycursor = mydb.cursor(dictionary=True);
	mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
	myresult = mycursor.fetchone();
	mydb.close();
	cont_loop = (myresult["settings_value"] == 1);
	while cont_loop:
		show_msg("Bio_snapshot: On");
		time.sleep(1)
		mydb = mysql.connector.connect(**DBconfig);
		mycursor = mydb.cursor(dictionary=True);
		mycursor.execute("SELECT `t_username` FROM `twitter_skip` ORDER BY `ts_id` ASC;");
		twitter_skipped = mycursor.fetchall();
		mycursor.execute("SELECT `filename` FROM `downloaded` ORDER BY `d_id` ASC;");
		already_downloaded = mycursor.fetchall();
		skip_list = [list(x.values())[0] for x in twitter_skipped] + [list(x.values())[0] for x in already_downloaded];
		sql_not = "";
		if len(skip_list):
			sql_not = "WHERE `t_username` NOT IN ({})".format(", ".join(["'{}'".format(x) for x in skip_list]));
		mycursor.execute("SELECT `t_username` FROM `twitter` {} ORDER BY `twit_id` ASC;".format(sql_not));
		all_user_results = mycursor.fetchall();
		mydb.close();
		if len(all_user_results):
			for i,x in enumerate(all_user_results):
				u = x["t_username"];
				if u == "":
					continue;
				with sync_playwright() as p:
					ua = (
						"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
						"AppleWebKit/537.36 (KHTML, like Gecko) "
						"Chrome/69.0.3497.100 Safari/537.36"
					)
					browser = p.chromium.launch();
					page = browser.new_page(user_agent=ua);
					show_msg("{}/{} - Opening https://twitter.com/{}".format(i+1,len(all_user_results),u));
					page.goto("https://twitter.com/{}".format(u), wait_until="domcontentloaded");
					page.wait_for_selector('img');
					img_elem = page.query_selector('[href="/{}/photo"] img'.format(u));
					if img_elem is not None:
						img_down(img_elem.get_attribute('src'), u);
					else:
						if page.query_selector("span :text('Yes, view profile')"):
							show_msg("PFP Blocked");
							page.locator("span :text('Yes, view profile')").click()
							page.mouse.wheel(0, -15000)
						else:
							show_msg("PFP Missing");
							mydb = mysql.connector.connect(**DBconfig);
							mycursor = mydb.cursor(dictionary=True, buffered=True);
							sql_query = f"INSERT INTO `twitter_skip` (`ts_id`, `t_username`) VALUES (NULL, %(t_username)s)";
							mycursor.execute(sql_query, {"t_username": u});
							mydb.commit();
							mydb.close();
							continue;
						img_elem = page.query_selector('[href="/{}/photo"] img'.format(u));
						img_down(img_elem.get_attribute('src'), u);

					mydb = mysql.connector.connect(**DBconfig);
					mycursor = mydb.cursor(dictionary=True, buffered=True);
					sql_query = f"SELECT `path` FROM `paths` WHERE `action`= 'hide' ORDER BY `p_id` ASC;";
					mycursor.execute(sql_query);
					hide_paths_r =  mycursor.fetchall();
					mydb.close();

					for x in hide_paths_r:
						hide_elem_JSxpath(page, x["path"]);

					page.screenshot(path="{}/{}.png".format(required_folders["shots"], u))
					html_str = page.query_selector('html').inner_html();
					with open("{}/{}.html".format(required_folders["cache"], u), "w") as text_file:
						text_file.write(html_str)
					browser.close()

				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				sql_query = f"INSERT INTO `downloaded` (`d_id`, `proj_id`, `filename`) VALUES (NULL, 2, %(filename)s)";
				mycursor.execute(sql_query, {"filename": u});
				mydb.commit();
				mydb.close();
				show_msg("{} Saved".format(u));
				wait_time = random.randint(15, 65);
				show_msg("Waiting: {} Sec".format(wait_time));
				time.sleep(wait_time);

				mydb = mysql.connector.connect(**DBconfig);
				mycursor = mydb.cursor(dictionary=True);
				mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = 'bio_snapshot'");
				myresult = mycursor.fetchone();
				mydb.close();
				cont_loop = (myresult["settings_value"] == 1);
				if not cont_loop:
					show_msg("Quiting");
					break;
		else:
			break;

	show_msg("Done");

except Exception as e:
	logging.debug("----------");
	logging.error(e);
	logging.debug("----------");
	print(e, flush=True);
	while KEEP_ALIVE:
		print("Debug mode", flush=True);
		time.sleep(60);