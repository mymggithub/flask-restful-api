#!/bin/sh
docker exec -it simple-api-mysql_db-1 bash -c "printf '[mysqldump]\npassword=pass123word\n' > /bkup/.my.cnf && cd bkup && chmod 006 .my.cnf && mysqldump --defaults-file=/bkup/.my.cnf --all-databases --single-transaction --quick --lock-tables=false > full-backup-$(date +%F).sql -u root && chmod 777 .my.cnf"
rm ./bkup/.my.cnf