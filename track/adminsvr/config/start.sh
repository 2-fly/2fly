#!/bin/bash

DIR=$(readlink -f $(dirname $0))

service nginx restart
cd ${DIR}/../
./run_adminsvr.sh

