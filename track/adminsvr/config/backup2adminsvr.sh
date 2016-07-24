#!/bin/bash

ipaddr=$1
staticrootdir='/root/massival'
backupdir='/data/massival'

mkdir -p ${backupdir}/rids
mkdir -p ${backupdir}/cids
mkdir -p ${backupdir}/postback
mkdir -p ${backupdir}/warn

rsync -avz ${ipaddr}:${staticrootdir}/rids/  ${backupdir}/rids/
rsync -avz ${ipaddr}:${staticrootdir}/cids/  ${backupdir}/cids/
rsync -avz ${ipaddr}:${staticrootdir}/postback/  ${backupdir}/postback/
rsync -avz ${ipaddr}:${staticrootdir}/warn/  ${backupdir}/warn/

