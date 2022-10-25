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
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(filename="log/default.log");
logging.getLogger().setLevel(logging.DEBUG);
logging.getLogger().setLevel(logging.INFO);

def show_msg(msg):
	logging.info(msg);
	print(msg, flush=True);

class MyPlaywright:
	required_folders = {
		"log":"log",
		"pics":"pics",
		"shots":"pics/shots",
		"pfp":"pics/pfp",
		"cache":"cache"
	};
	DBconfig = {
		"host":"mysql_db", 
		"user":"root", 
		"passwd":"pass123word",
		"database":"yiiadv"
	};
	ua = (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/69.0.3497.100 Safari/537.36"
	);
	page = {};
	browser = {};
	def __init__(self):
		self.load_required_dir();
		while self.get_setting("bio_snapshot"):
			show_msg("Bio_snapshot: On");
			time.sleep(1);
			usernames_list = self.get_usernames();
			if len(usernames_list):
				for i,user in enumerate(usernames_list):
					if user == "":
						continue;
					with sync_playwright() as p:
						self.browser = p.chromium.launch();
						self.page = self.browser.new_page(user_agent=self.ua);
						show_msg("{}/{} - Opening https://twitter.com/{}".format(i+1,len(usernames_list),user));
						self.page.goto("https://twitter.com/{}".format(user), wait_until="domcontentloaded");
						self.page.wait_for_selector('img');
						img_elem = self.page.query_selector('[href="/{}/photo"] img'.format(user));
						if img_elem is not None:
							self.download_img(img_elem.get_attribute('src'), user);
						else:
							if self.page.query_selector("span :text('Yes, view profile')"):
								show_msg("PFP Blocked");
								self.page.locator("span :text('Yes, view profile')").click()
								self.page.mouse.wheel(0, -15000)
							else:
								show_msg("PFP Missing");
								self.set_to_skip(user);
								continue;
							img_elem = self.page.query_selector('[href="/{}/photo"] img'.format(user));
							self.download_img(img_elem.get_attribute('src'), user);

						self.hide_xpaths();
						self.save(user);
						self.browser.close();
						wait_time = random.randint(15, 65);
						show_msg("Waiting: {} Sec".format(wait_time));
						time.sleep(wait_time);
			show_msg("Done");
		show_msg("Quiting");

	def load_required_dir(self):
		for dir_var in self.required_folders:
			if not os.path.exists(self.required_folders[dir_var]):
				os.mkdir(self.required_folders[dir_var]);

	def hide_elem_JSxpath(self, current_xpath):
		self.page.evaluate("""() =>  document.evaluate(`{}`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.display = "none" """.format(current_xpath));

	def download_img(self, url, filename):
		response  = requests.get(url).content 
		image_file = io.BytesIO(response)
		image  = Image.open(image_file).convert('RGB')
		split_tup = os.path.splitext(url);
		show_msg( "{}/{}{}".format(self.required_folders["pfp"], filename, str(split_tup[1])) );
		image.save("{}/{}{}".format(self.required_folders["pfp"], filename, str(split_tup[1])) , "JPEG");
		show_msg("Downladed PFP");

	def get_setting(self, name):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute("SELECT * FROM `settings` WHERE `settings_name` = '{}'".format(name));
			r = mycursor.fetchone();
			mydb.close();
			if r is not None and "settings_value" in r:
				return (r["settings_value"] == 1);
			return r;
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def get_skip_list(self):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute("SELECT `t_username` FROM `twitter_skip` ORDER BY `ts_id` ASC;");
			twitter_skipped = mycursor.fetchall();
			mycursor.execute("SELECT `filename` FROM `downloaded` ORDER BY `d_id` ASC;");
			already_downloaded = mycursor.fetchall();
			mydb.close();
			return [list(x.values())[0] for x in twitter_skipped] + [list(x.values())[0] for x in already_downloaded];
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def get_usernames(self):
		skip_list = self.get_skip_list();
		sql_not = "";
		if len(skip_list):
			sql_not = "WHERE `t_username` NOT IN ({})".format(", ".join(["'{}'".format(x) for x in skip_list]));
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute("SELECT `t_username` FROM `twitter` {} ORDER BY `twit_id` ASC;".format(sql_not));
			r = mycursor.fetchall();
			mydb.close();
			return [list(x.values())[0] for x in r];
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def set_to_skip(self, username):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"INSERT IGNORE INTO `twitter_skip` (`ts_id`, `t_username`) VALUES (NULL, %(t_username)s)";
			mycursor.execute(sql_query, {"t_username": username});
			mydb.commit();
			mydb.close();
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def hide_xpaths(self):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"SELECT `path` FROM `paths` WHERE `action`= 'hide' ORDER BY `p_id` ASC;";
			mycursor.execute(sql_query);
			hide_paths_r =  mycursor.fetchall();
			mydb.close();

			for x in hide_paths_r:
				self.hide_elem_JSxpath(x["path"]);
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def save(self, filename):
		if not os.path.exists("{}/{}.png".format(self.required_folders["shots"], filename)):
			self.page.screenshot(path="{}/{}.png".format(self.required_folders["shots"], filename));
		if not os.path.exists("{}/{}.html".format(self.required_folders["cache"], filename)):
			html_str = self.page.query_selector('html').inner_html();
			with open("{}/{}.html".format(self.required_folders["cache"], filename), "w") as text_file:
				text_file.write(html_str)

		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"INSERT IGNORE INTO `downloaded` (`d_id`, `proj_id`, `filename`) VALUES (NULL, 2, %(filename)s)";
			mycursor.execute(sql_query, {"filename": filename});
			mydb.commit();
			mydb.close();
			show_msg("{} Saved".format(filename));
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

if __name__ == '__main__':
	KEEP_ALIVE = False;
	try:
		pw = MyPlaywright();
	except Exception as e:
		logging.debug("----------");
		logging.error(e);
		logging.debug("----------");
		print(e, flush=True);
		while KEEP_ALIVE:
			print("Debug mode", flush=True);
			time.sleep(60);