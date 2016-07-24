#!/bin/bash

local_dir='/data/massival'
remote_dir='/data/massival_v3'


rsync -avz ${local_dir}/rids/*    eudb:${remote_dir}/rids/
rsync -avz ${local_dir}/cids/*    eudb:${remote_dir}/cids/
rsync -avz ${local_dir}/postback/*    eudb:${remote_dir}/postback/
rsync -avz ${local_dir}/warn/*   eudb:${remote_dir}/warn/

