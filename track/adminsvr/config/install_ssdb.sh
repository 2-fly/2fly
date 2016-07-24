#!/bin/bash

########
## Basic Install
########

yum install git make automake gcc gcc-c++ kernel-devel python python-devel mysql mysql-server mysql-devel MySQL-python -y
yum install libxml2 libxml2-devel libxslt-devel -y

wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py --no-check-certificate
python get-pip.py
export PATH=$PATH:/usr/local/bin
ln -s /usr/local/bin/pip /usr/bin/pip
pip install awscli uwsgi virtualenv supervisor sqlalchemy geoip2 PyCrypto pyyaml redis requests flask flask-sqlalchemy mysql-python raven blinker init mako pymysql pywurfl newrelic ujson termcolor route53
ln -s /usr/local/bin/uwsgi /usr/bin/uwsgi
ln -s /usr/local/bin/newrelic-admin /usr/bin/newrelic-admin


########
## Time
########

\cp /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime
echo 'ZONE="Asia/Hong_Kong"
UTC=false
ARC=false' > /etc/sysconfig/clock
yum install ntpdate -y
ntpdate us.pool.ntp.org

echo "* soft nofile 102400
* hard nofile 204800" >> /etc/security/limits.conf

ulimit -n 102400


########
## NGINX
########
DIR=$(readlink -f $(dirname $0))
rpm -ivh http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
yum install nginx -y
mkdir -p /media/ephemeral0/nginx_log
\cp ${DIR}/nginx.conf /etc/nginx/nginx.conf
\cp ${DIR}/adminsvr.conf /etc/nginx/conf.d/adminsvr.conf
echo "bash ${DIR}/start.sh" >> /etc/rc.local

service nginx restart

mkdir -p /media/ephemeral0/uwsgi

########
## SSDB
########

rm -rf /tmp/master.zip
rm -rf /tmp/ssdb-master
cd /tmp

wget --no-check-certificate https://github.com/ideawu/ssdb/archive/master.zip
unzip master
cd ssdb-master
make
# optional, install ssdb in /usr/local/ssdb
sudo make install

mkdir -p /root/data
mkdir -p /media/ephemeral0/ssdb
export PATH=$PATH:/usr/local/ssdb
#ssdb-server

DIR=$(readlink -f $(dirname $0))
cp -f ${DIR}/ssdb.sh /etc/init.d/ssdb
chkconfig --add ssdb
service ssdb restart

##########################################################################


#######
## NewRelic
#######
rpm -Uvh http://download.newrelic.com/pub/newrelic/el5/i386/newrelic-repo-5-3.noarch.rpm
yum install newrelic-sysmond -y
nrsysmond-config --set license_key=cee00b7aa24168adfe5332042e0db6cb649039c6
/etc/init.d/newrelic-sysmond start
chkconfig newrelic-sysmond on


