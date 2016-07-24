#!/bin/bash

ipaddr=$1
staticrootdir='/media/ephemeral0'
backupdir='/root/massival'

mkdir -p ${backupdir}/rids
mkdir -p ${backupdir}/cids
mkdir -p ${backupdir}/postback
mkdir -p ${backupdir}/warn

rsync -avz ${ipaddr}:${staticrootdir}/rawdata/rids/  ${backupdir}/rids/
rsync -avz ${ipaddr}:${staticrootdir}/rawdata/cids/  ${backupdir}/cids/
rsync -avz ${ipaddr}:${staticrootdir}/rawdata/postback/  ${backupdir}/postback/
rsync -avz ${ipaddr}:${staticrootdir}/rawdata/warn/  ${backupdir}/warn/


