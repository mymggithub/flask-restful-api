screen -ls
detach - Ctrl+A and D


jupyter notebook --allow-root --ip 0.0.0.0 --port 8888


.close()


logging.basicConfig(filename="log/default.log", level=logging.DEBUG);
log = logging.getLogger('werkzeug');
log.setLevel(logging.ERROR);



python-is-python3
https://kb.vmware.com/s/article/60262


https://askcodes.net/coding/vmhgfs-fuse-at-boot-with-vmware-windows-8-1-host-and-ubuntu-16-04-guest

https://www.youtube.com/watch?v=ati2jtyjCq0&ab_channel=BrainI%2FO

https://stackoverflow.com/questions/38737254/vmhgfs-fuse-at-boot-with-vmware-windows-8-1-host-and-ubuntu-16-04-guest

https://communities.vmware.com/t5/VMware-Workstation-Pro/Shared-folders-not-available-on-Linux-guests-after-upgrading-to/td-p/1404693

vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other

.host:/ /mnt/hgfs fuse.vmhgfs-fuse allow_other 0 0


/usr/bin/vmhgfs-fuse .host:/ /mnt/hgfs -o subtype=vmhgfs-fuse,allow_other

sudo umount /mnt/hgfs

sudo apt-get install open-vm-tools-desktop


sudo apt-get install open-vm-tools


docker-compose up


docker build -t flask-api .
docker run -p 5000:5000 --name flack-api-c -it flask-api



/home/pwuser
docker build -t pw .

docker run -v "$PWD":/home/pwuser --name pw-c -it pw

docker run -v "$PWD":/home/pwuser -p 8888:8888 --name pw-c -it pw

docker exec -it simple-api-pw_snapshot-1 /bin/bash

docker start simple-api-pw_snapshot-1

jupyter notebook --allow-root --ip 0.0.0.0 --port 8888


https://stackoverflow.com/questions/67255873/how-can-i-remove-m-character-which-is-showing-in-my-file-on-git

https://askubuntu.com/questions/304999/not-able-to-execute-a-sh-file-bin-bashm-bad-interpreter

sed -i -e 's/\r$//' create_mgw_3shelf_6xIPNI1P.sh



page.eval_on_selector('//*[@id="layers"]/div', "element => element.style.display = 'hidden'")
page.evaluate(
"""
function getElementByXpath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}
getElementByXpath("//html[1]/body[1]/div[1]").style.display = "none"
""")
print(page.query_selector('//*[@id="layers"]/div').inner_html())
.querySelector('xpath=..')
page.evaluate('$("span:contains(Don???t miss what???s happening)").parent().parent().parent().parent().remove()')


docker run --rm --volumes-from simple-api-mysql_db-1 -v ~/backup:/backup ubuntu bash -c ???cd /var/lib/ghost/content && tar cvf /backup/ghost-site.tar .???



docker run --rm --volumes-from simple-api-mysql_db-1 -v db_data:/var/lib/mysql -v ~/backup:/backup -it mysql bash -l


printf '[mysqldump]\npassword=pass123word\n' > .my.cnf




mysqldump --defaults-file=/backup/.my.cnf ???u root yiiadv > my_db.sql


mysqldump --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root

command: --default-authentication-plugin=mysql_native_password


#(CASE WHEN (`following`-`followers`) > 0 THEN FLOOR((`following`-`followers`)*(100/`following`)) ELSE 0 END) as `will_f`, (CASE WHEN (`followers`-`following`) > 0 THEN FLOOR((`followers`-`following`)*(100/`followers`)) ELSE 0 END) as `wont_f`





f"`description` = '%(description)s'"%{"description": desc}
"SELECT * FROM `twitter` WHERE t_username LIKE '{0}'".format(t_username)


page.goto("file:/root/Desktop/__FoxyBaby__.html", wait_until="domcontentloaded");

html.tostring(root, pretty_print=True)