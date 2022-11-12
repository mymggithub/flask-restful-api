#!/usr/bin/python
import os, logging, time, random, requests, re, threading, json
from playwright.sync_api import sync_playwright
import mysql.connector, io
from lxml import html
from PIL import Image
from PIL import ImageChops


logging.basicConfig(filename="log/default.log");
logging.getLogger().setLevel(logging.DEBUG);
logging.getLogger().setLevel(logging.INFO);

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def show_msg(msg):
	logging.info(msg);
	print(msg, flush=True);

class MyPlaywright:
	DBconfig = {};
	required_folders = {
		"log":"log",
		"pics":"pics",
		"shots":"pics/shots",
		"pfp":"pics/pfp",
		"test_with":"pics/test_with",
		"cache":"cache",
	};
	ua = (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
		"AppleWebKit/537.36 (KHTML, like Gecko) "
		"Chrome/69.0.3497.100 Safari/537.36"
	);
	page = {};
	browser = {};
	workflow_id = 1;
	proj_id = 1;
	def __init__(self, proj_id):
		if os.path.exists("config/db.json"):
			self.DBconfig = json.load(open('config/db.json'));

		self.proj_id = proj_id;
		self.load_required_dir();
		# self.cache_bio();
		# self.set_bio_data();
		# while self.get_setting("bio_snapshot"):
		# 	time.sleep(60);
		# t1 = threading.Thread(target=self.cache_bio).start()
		# t2 = threading.Thread(target=self.set_bio_data).start()


	def get_project(self):
		mydb = mysql.connector.connect(**self.DBconfig);
		if mydb.is_connected():
			mycursor = mydb.cursor(dictionary=True);
			mycursor.execute(f"""SELECT `proj_username`, `main_proj_site` FROM `project` WHERE `proj_id` = '{self.proj_id}';""");
			r = mycursor.fetchone();
			mydb.close();
			return r;
		else:
			logging.debug("----------");
			logging.error("MySQL Not connected");
			logging.debug("----------");

	@threaded
	def account_actions(self):
		proj = self.get_project();
		if len(proj):
			show_msg(proj["proj_username"]);
			username = proj["main_proj_site"];
			passwd = "";
			tmp_code = "";
			if proj["main_proj_site"] == "twitter":
				with sync_playwright() as p:
					self.acc_browser = p.chromium.launch();
					self.acc_context = self.acc_browser.new_context();
					self.acc_page = self.acc_context.new_page();
					self.acc_page.goto('https://twitter.com/i/flow/login');
					self.acc_page.wait_for_selector('[autocomplete="username"]');
					self.acc_page.query_selector('[autocomplete="username"]').fill(username);
					self.acc_page.get_by_text('Next').click();
					self.acc_page.wait_for_selector('[type="password"]');
					self.acc_page.query_selector('[type="password"]').fill(passwd);
					self.acc_page.get_by_text('Log in').click();
					time.sleep(3);
					while self.acc_page.evaluate("""() =>  window.location.href""") != 'https://twitter.com/home' and self.acc_page.get_by_text('Enter your verification code').count():
						self.acc_page.query_selector('[inputmode="numeric"]').fill(tmp_code);
						self.acc_page.get_by_text('Next').click();
						time.sleep(10);
					self.acc_page.get_by_text('Profile').click();
					self.acc_page.get_by_text('Following').click();
					start_h = 0;
					while True:
						scroll_r = self.acc_page.evaluate("""() =>  {
						function softScroll(elementY, duration) { 
						  var startingY = window.pageYOffset;
						  var diff = elementY - startingY;
						  var start;
						  window.requestAnimationFrame(function step(timestamp) {
						    if (!start) start = timestamp;
						    var time = timestamp - start;
						    var percent = Math.min(time / duration, 1);
						    window.scrollTo(0, startingY + diff * percent);
						    if (time < duration) {
						      window.requestAnimationFrame(step);
						    }
						  })
						}
						arr = [].slice.call(document.querySelectorAll('[data-testid="UserCell"] div[dir="ltr"]'))
						usernames = arr.map(x => x.innerText.replace("@",""))
						pos_arr = arr.map(x => (window.pageYOffset || document.documentElement.scrollTop)  - (document.documentElement.clientTop || 0)+x.getBoundingClientRect().top).sort((a,b)=> a-b)
						last_high_num = pos_arr.slice(-1)
						softScroll(last_high_num, 2500)
						return {"last_height":last_high_num[0], "usernames":usernames}
						} """);
						time.sleep(5);
						if scroll_r["last_height"] != start_h:
							start_h = scroll_r["last_height"];
						else:
							break;



	@threaded
	def set_bio_data(self):
		while self.get_setting("get_cache_info"):
			# show_msg("Setting Bio Data: Loading");
			mydb = mysql.connector.connect(**self.DBconfig);
			if mydb.is_connected():
				show_msg("Setting Bio Data: On");
				time.sleep(1);
				mycursor = mydb.cursor(dictionary=True, buffered=True);
				mycursor.execute(f"""SELECT `t_username` FROM `proj_data` WHERE `cached` = 1 AND  `scanned` = 0;""");
				r = mycursor.fetchall();
				sql_query = f"""SELECT `path`, `name` FROM `paths` WHERE `action`= 'value' ORDER BY `p_id` ASC;""";
				mycursor.execute(sql_query);
				value_paths_r =  mycursor.fetchall();
				mydb.close();
				cached_list = [list(x.values())[0] for x in r];
				show_msg(f"Number of data to set: {len(cached_list)}");
				for username in cached_list:
					data = {};
					blank_pfp = f"""{self.required_folders["test_with"]}/blank_pfp.jpg""";
					u_pfp = f"""{self.required_folders["pfp"]}/{username}.jpg""";
					data["blank_pfp"] = 1;
					if os.path.exists(u_pfp):
						image_one = Image.open(u_pfp);
						image_two = Image.open(blank_pfp);
						diff = ImageChops.difference(image_one, image_two);
						data["blank_pfp"] = 1 if not bool(diff.getbbox()) else 0;
					u_path = f"""{self.required_folders["cache"]}/{username}.html""";
					show_msg(f"""{cached_list.index(username)}/{len(cached_list)} - {u_path} File exists: {os.path.exists(u_path)}""");
					if os.path.exists(u_path):
						root = html.parse(u_path);
						for x in value_paths_r:
							try:
								x_value = root.xpath(x["path"]);
								if len(x_value):
									if x["name"] == "following" or x["name"] == "followers":
										x_value = "".join(x_value);
										x_value = re.sub("[.][0-9]{1}[K]", "{}00".format(x_value.split(".")[-1].replace("K","")), x_value); #for 17.4K or something
										data[x["name"]] = int(x_value.replace("K", "000").replace(",", "").replace(" Following", "").replace(" Followers", ""));
									if x["name"] == "description":
										desc = str("".join(x_value)).encode("ascii", "ignore").decode().translate(str.maketrans({"'":"\\'"}));
										data[x["name"]] = desc;
								else:
									if x["name"] == "following" or x["name"] == "followers":
										if x["name"] not in data or data[x["name"]] == "":
											data[x["name"]] = 0;
									else:
										data[x["name"]] = '';
							except Exception as e:
								if x["name"] == "following" or x["name"] == "followers":
									if x["name"] not in data or data[x["name"]] == "":
										data[x["name"]] = 0;
								else:
									data[x["name"]] = '';
						try:
							mydb = mysql.connector.connect(**self.DBconfig);
							mycursor = mydb.cursor(dictionary=True, buffered=True);
							data["scanned"] = 1;
							sql_query = """UPDATE `proj_data` SET {} WHERE `t_username` LIKE '{}';""".format(", ".join([f""" `{x}` = '%s'""" for x in data]), username);
							# show_msg(sql_query%tuple([data[x] for x in data]));
							mycursor.execute(sql_query%tuple([data[x] for x in data]));
							mydb.commit();
							mydb.close();
							# time.sleep(1);
						except Exception as e:
							pass
						if bool(mycursor.rowcount):
							show_msg(f"""{cached_list.index(username)+1}/{len(cached_list)} - {username} data scanned""");
							# show_msg(data);
							time.sleep(1);

			else:
				logging.debug("----------");
				logging.error("MySQL Not connected");
				logging.debug("----------");

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
			mycursor.execute(f"""SELECT `t_username` FROM `proj_data` WHERE `skip` = 1 OR `cached` = 1 ORDER BY `twit_id` ASC;""");
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
			mycursor.execute(f"""SELECT `t_username` FROM `proj_data` {sql_not} ORDER BY `twit_id` ASC;""");
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
			sql_query = f"UPDATE `proj_data` SET `skip` = 1 WHERE `t_username` = %(t_username)s;";
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
			sql_query = f"""UPDATE `proj_data` SET `cached` = 1 WHERE `t_username` = %(t_username)s;""";
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

	@threaded
	def cache_bio(self):
		while self.get_setting("bio_snapshot"):
			time.sleep(1);
			# show_msg("Bio_snapshot: On");
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
					wait_time = random.randint(30, 60);
					show_msg(f"Waiting: {wait_time} Sec");
					time.sleep(wait_time);
			show_msg("Done");

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
		t1 = pw.cache_bio();
		t2 = pw.set_bio_data();
		t1.join();
		t2.join();
		show_msg("Quiting");
	except Exception as e:
		logging.debug("----------");
		logging.error(e);
		logging.debug("----------");
		print(e, flush=True);
		while KEEP_ALIVE:
			print("Debug mode", flush=True);
			time.sleep(60);