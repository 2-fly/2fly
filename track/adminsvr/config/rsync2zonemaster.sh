#!/bin/bash

ipaddr=$1
ASSETS_DIR='/media/ephemeral0'

mkdir -p ${ASSETS_DIR}/assets
chmod -R 755 ${ASSETS_DIR}/assets
rsync -avz --exclude='*.zip' ${ASSETS_DIR}/assets ${ipaddr}:${ASSETS_DIR}/

