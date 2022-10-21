#!/bin/sh
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