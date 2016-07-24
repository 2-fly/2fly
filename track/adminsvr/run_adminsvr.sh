#!/bin/bash

DIR=$(readlink -f $(dirname $0))
PROGRAM_NAME='adminsvr'
ps aux | grep uwsgi | grep ${PROGRAM_NAME} | awk '{printf("kill -9 %s\n", $2)}' | sh
sleep 1

#sysctl -w net.core.somaxconn=100000
echo 65500 >   /proc/sys/net/core/somaxconn
sysctl -w fs.file-max=1617055

mkdir -p /var/log/uwsgi
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uwsgi --socket 127.0.0.1:3131 --file ${DIR}/${PROGRAM_NAME}.py --callable app --listen 65500 --processes 8 --daemonize2 /var/log/uwsgi/${PROGRAM_NAME}.log --pidfile /var/run/${PROGRAM_NAME}.pid --enable-threads --master --die-on-term
