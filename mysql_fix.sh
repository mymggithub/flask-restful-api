#!/bin/sh
docker run -d -v /host/path/:/var/lib/mysql mysql:latest --innodb-flush-method=O_DSYNC