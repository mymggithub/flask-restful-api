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