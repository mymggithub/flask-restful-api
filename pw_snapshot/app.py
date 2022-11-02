#!/usr/bin/python
import os, logging, time, random, requests
from playwright.sync_api import sync_playwright
import mysql.connector, io
from lxml import html
from PIL import Image

logging.basicConfig(filename="log/default.log");
logging.getLogger().setLevel(logging.DEBUG);
logging.getLogger().setLevel(logging.INFO);

def show_msg(msg):
	logging.info(msg);
	print(msg, flush=True);

class MyPlaywright:
	DBconfig = { "host":"mysql-db", "user":"root", "passwd":"pass123word", "database":"yiiadv" };
	required_folders = {
		"log":"log",
		"pics":"pics",
		"shots":"pics/shots",
		"pfp":"pics/pfp",
		"cache":"cache"
	};
	ua = (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/69.0.3497.100 Safari/537.36"
	);
	page = {};
	browser = {};
	workflow_id = 1;
	def __init__(self, workflow_id):
		self.workflow_id = workflow_id;
		self.load_required_dir();
		while self.get_setting("bio_snapshot"):
			show_msg("Bio_snapshot: On");
			time.sleep(1);
			usernames_list = self.get_usernames();
			if len(usernames_list):
				for i,user in enumerate(usernames_list):
					if self.get_setting("restart_bio"):
						self.set_setting("restart_bio", False);
						show_msg("Restarting");
						break;
					if user == "":
						continue;
					if not self.load_browser(i, usernames_list, user):
						continue;
					wait_time = random.randint(15, 65);
					show_msg(f"Waiting: {wait_time} Sec");
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
		# split_tup = os.path.splitext(url);
		show_msg( f"""{self.required_folders["pfp"]}/{filename}.jpg""" );
		image.save( f"""{self.required_folders["pfp"]}/{filename}.jpg""" );
		show_msg("Downladed PFP");

	def get_setting(self, name):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute(f"""SELECT * FROM `settings` WHERE `settings_name` = '{name}';""");
			r = mycursor.fetchone();
			mydb.close();
			if r is not None and "settings_value" in r:
				return (r["settings_value"] == 1);
			return r;
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def set_setting(self, name, value):
		if value:
			value = 1;
		else:
			value = 0;
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute(f"""UPDATE `settings` SET `settings_value` = '{value}' WHERE `settings_name` = '{name}';""");
			mydb.commit();
			mydb.close();
			return True;
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def get_skip_list(self):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute(f"""SELECT `t_username` FROM `twitter` WHERE `skip` = 1 OR `cached` = 1 ORDER BY `twit_id` ASC;""");
			twitter_skipped = mycursor.fetchall();
			mydb.close();
			return [list(x.values())[0] for x in twitter_skipped];
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def get_usernames(self):
		skip_list = self.get_skip_list();
		sql_not = "";
		if len(skip_list):
			sql_not = "WHERE `t_username` NOT IN ({})".format(", ".join([f"'{x}'" for x in skip_list]));
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute(f"""SELECT `t_username` FROM `twitter` {sql_not} ORDER BY `twit_id` ASC;""");
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
			sql_query = f"UPDATE `twitter` SET `skip` = 1 WHERE `t_username` = %(t_username)s;";
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
			sql_query = f"""SELECT `path` FROM `paths` WHERE `action`= 'hide' ORDER BY `p_id` ASC;""";
			mycursor.execute(sql_query);
			hide_paths_r =  mycursor.fetchall();
			mydb.close();

			for x in hide_paths_r:
				self.hide_elem_JSxpath(x["path"]);
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def save(self, username):
		if not os.path.exists(f"""{self.required_folders["shots"]}/{username}.png"""):
			self.page.screenshot(path=f"""{self.required_folders["shots"]}/{username}.png""");
		if not os.path.exists(f"""{self.required_folders["cache"]}/{username}.html"""):
			html_str = self.page.query_selector('html').inner_html();
			with open(f"""{self.required_folders["cache"]}/{username}.html""", "w") as text_file:
				text_file.write(html_str)

		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""UPDATE `twitter` SET `cached` = 1 WHERE `t_username` = %(t_username)s;""";
			mycursor.execute(sql_query, {"t_username": username});
			mydb.commit();
			mydb.close();
			show_msg(f"{username} Saved");
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def get_workflow_url(self):
		sql_query = "";
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True, buffered=True);
			sql_query = f"""SELECT `wf_url` FROM `workflow_main` WHERE `wfm_id` = '{self.workflow_id}';""";
			mycursor.execute(sql_query);
			r =  mycursor.fetchall();
			mydb.close();
			return [list(x.values())[0] for x in r];
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	def load_browser(self, i, usernames_list, user):
		url = "";
		url_arr = self.get_workflow_url();
		if len(url_arr) and type(url_arr) is list:
			url = url_arr[0]
		with sync_playwright() as p:
			self.browser = p.chromium.launch();
			self.page = self.browser.new_page(user_agent=self.ua);
			show_msg(f"{i+1}/{len(usernames_list)} - Opening {url.format(user)}");
			self.page.goto(url.format(user), wait_until="domcontentloaded");
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
					return False;
				img_elem = self.page.query_selector('[href="/{}/photo"] img'.format(user));
				self.download_img(img_elem.get_attribute('src'), user);

			self.hide_xpaths();
			self.save(user);
			self.browser.close();
			return True;

if __name__ == '__main__':
	KEEP_ALIVE = False;
	try:
		pw = MyPlaywright(1);
	except Exception as e:
		logging.debug("----------");
		logging.error(e);
		logging.debug("----------");
		print(e, flush=True);
		while KEEP_ALIVE:
			print("Debug mode", flush=True);
			time.sleep(60);