#!/bin/sh
mkdir bkup
docker exec -it simple-api-mysql_db-1 bash -c "printf '[mysqldump]\npassword=pass123word\n' > /bkup/.my.cnf && chmod 006 /bkup/.my.cnf && mysqldump --defaults-file=/bkup/.my.cnf --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root"
docker-compose stop
docker rm simple-api-pw_snapshot-1
docker rm simple-api-phpmyadmin-1
docker rm simple-api-mysql_db-1
docker rm simple-api-flask-api-1
docker rmi simple-api-pw_snapshot
docker rmi simple-api-flask-api
docker rmi phpmyadmin
docker rmi mysql
docker volume rm simple-api_pw_log
docker volume rm simple-api_api_log
docker volume rm simple-api_db_data