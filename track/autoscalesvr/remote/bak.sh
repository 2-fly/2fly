

hostname=`hostname`

ndate=`date --date="-1 hour" +%Y%m%d%H-%s`
adate=`date --date="-1 hour" +%Y%m%d%H`
odate=`date --date="-2 hour" +%Y%m%d%H`

mv /media/ephemeral0/uwsgi_log/link_svr.log /media/ephemeral0/uwsgi_log/link_svr_${ndate}.log
touch /media/ephemeral0/uwsgi_log/.link_rotate

mv /media/ephemeral0/uwsgi_log/querysvr.log /media/ephemeral0/uwsgi_log/querysvr_${ndate}.log
touch /media/ephemeral0/uwsgi_log/.query_rotate

mv /media/ephemeral0/nginx_log/access.log  /media/ephemeral0/nginx_log/access_${ndate}.log
mv /media/ephemeral0/nginx_log/error.log  /media/ephemeral0/nginx_log/error_${ndate}.log
/etc/init.d/nginx reload

cd /media/ephemeral0/nginx_log
zip /media/ephemeral0/nginx-access-${hostname}-${ndate}.zip access_${ndate}.log
zip /media/ephemeral0/nginx-error-${hostname}-${ndate}.zip error_${ndate}.log

cd /media/ephemeral0/uwsgi_log
zip /media/ephemeral0/link_svr-${hostname}-${ndate}.zip link_svr_${ndate}.log
zip /media/ephemeral0/querysvr-${hostname}-${ndate}.zip querysvr_${ndate}.log


aws s3 cp /media/ephemeral0/nginx-access-${hostname}-${ndate}.zip s3://v3-massival/nginxaccess/${adate}/
aws s3 cp /media/ephemeral0/nginx-error-${hostname}-${ndate}.zip s3://v3-massival/nginxerror/${adate}/
aws s3 cp /media/ephemeral0/link_svr-${hostname}-${ndate}.zip s3://v3-massival/linksvr/${adate}/
aws s3 cp /media/ephemeral0/querysvr-${hostname}-${ndate}.zip s3://v3-massival/querysvr/${adate}/


adate=`date +%Y%m%d%H`
cd /media/ephemeral0/rawdata

zip -r /media/ephemeral0/hourraw-${hostname}-${adate}.zip cids/*${adate}*  postback/*${adate}*  rids/*${adate}*  warn/*${adate}*

aws s3 cp /media/ephemeral0/hourraw-${hostname}-${adate}.zip s3://v3-massival/hourraw/${adate}/


