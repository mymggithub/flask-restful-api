#!/bin/sh
docker rm simple-api-pw_snapshot-1
docker rmi simple-api-pw_snapshot
docker volume rm simple-api_pw_log