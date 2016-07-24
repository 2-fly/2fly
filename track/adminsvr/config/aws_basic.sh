#!/bin/bash

#region=sng
#newhost=`hostname | sed "s/ip/${region}/g"`
#hostname $newhost

yum install git make automake gcc gcc-c++ kernel-devel python python-devel mysql MySQL-python mysql-devel -y 

wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py --no-check-certificate
python get-pip.py
export PATH=$PATH:/usr/local/bin
ln -s /usr/local/bin/pip /usr/bin/pip
pip install awscli uwsgi virtualenv supervisor sqlalchemy geoip2 PyCrypto pyyaml redis requests flask flask-sqlalchemy mysql-python raven blinker init mako pymysql pywurfl newrelic ujson termcolor
ln -s /usr/local/bin/uwsgi /usr/bin/uwsgi
ln -s /usr/local/bin/newrelic-admin /usr/bin/newrelic-admin

########
## NGINX
########
DIR=$(readlink -f $(dirname $0))
yum install nginx -y
\cp ${DIR}/nginx.conf /etc/nginx/nginx.conf
\cp ${DIR}/adminsvr.conf /etc/nginx/conf.d/default.conf
echo "bash ${DIR}/start.sh" >> /etc/rc.local

#######
## NewRelic
#######
rpm -Uvh http://download.newrelic.com/pub/newrelic/el5/i386/newrelic-repo-5-3.noarch.rpm
yum install newrelic-sysmond -y
nrsysmond-config --set license_key=cee00b7aa24168adfe5332042e0db6cb649039c6
/etc/init.d/newrelic-sysmond start
chkconfig newrelic-sysmond on

echo "* soft nofile 102400
* hard nofile 204800" >> /etc/security/limits.conf

mkdir /media/ephemeral0/uwsgi_log
mkdir /media/ephemeral0/nginx_log
touch /media/ephemeral0/uwsgi_log/.query_rotate
touch /media/ephemeral0/uwsgi_log/.link_rotate

bash ${DIR}/rsync.sh
echo "1 * * * * bash ${DIR}/hourrotate.sh > /dev/null 2>&1
* * * * * bash ${DIR}/rsync.sh > /dev/null 2>&1" >> /var/spool/cron/root
service crond restart

service nginx restart
cd ${DIR}/../
./run_link_svr.sh
cd ${DIR}/../../querysvr
./run_querysvr.sh

