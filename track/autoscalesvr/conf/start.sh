#!/bin/bash

DIR=$(readlink -f $(dirname $0))

service nginx restart
cd ${DIR}/../
./run_autos_svr.sh

