#!/bin/sh
docker-compose stop
docker rm pw-snapshot
docker rm simple-api-apache-ui-1
docker rm simple-api-phpmyadmin-1
docker rm simple-api-mysql-db-1
docker rm simple-api-flask-api-1
docker rmi simple-api-pw-snapshot
docker rmi simple-api-flask-api
docker rmi phpmyadmin
docker rmi mysql
docker rmi php:8.0-apache
docker volume rm simple-api_pw-log
docker volume rm simple-api_api-log
docker volume rm simple-api_db-data