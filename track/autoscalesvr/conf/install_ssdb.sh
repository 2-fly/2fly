#!/bin/bash

########
## Basic Install
########

region="us-west-1"

DIR=$(readlink -f $(dirname $0))
LOG_DIR="/var/log"
ASSETS_DIR="/media/ephemeral0/assets"


yum install git make automake gcc gcc-c++ kernel-devel python python-devel mysql-server mysql mysql-devel MySQL-python unzip expect nc -y

wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py --no-check-certificate
python get-pip.py
export PATH=$PATH:/usr/local/bin
ln -s /usr/local/bin/pip /usr/bin/pip
pip install awscli uwsgi virtualenv supervisor sqlalchemy geoip2 PyCrypto pyyaml redis requests flask flask-sqlalchemy mysql-python raven blinker init mako pymysql pywurfl newrelic ujson termcolor
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


########
## SSH
########


cp /home/ec2-user/.ssh/authorized_keys /root/.ssh/

sed -i "/PermitRootLogin/d" /etc/ssh/sshd_config

echo "PermitRootLogin yes
PermitRootLogin forced-commands-only" >> /etc/ssh/sshd_config

echo "StrictHostKeyChecking no
UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config



service sshd reload


mkdir -p /root/.ssh
echo "-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAg6HTfSZGGpJuTixyPI5ieiK/33LedB8KMVoYiSVqMYFXUBIUUdmPCdk5KCyY
tKdREXb2j9oreJzmjUYFjsmt9ecxAEDV20odSMrpJPTFEMj7VaevW1xbnH8df4eRk2uZ/GllD0lL
HjAo2Trb889ETxLowkRUXQM5rWtfS93JbQa20DI9LrUxDuDZQWjT6Qexm9b6HJf2fF+5/9nY35Mw
ZwpMsv+1kLjMOaRF/S5OawIGh2+8XhiG5cnshky+oJ8eUXLEpfZgdbnKfrlnju+z+CDPnN3gRO/r
b9gllNDCjkGzTMNw+SVEOv5gw2fLZlzK0upC+bX+hzzeL6RP9zKUmwIDAQABAoIBAGapzjLrqP2M
e2+JBsfoHTI47AEwrANROjfnlv9QKRTXVevjTenQjtkVjJiiv68WWAoRCJiFhiYZ6U8B78+/yGfj
mroh1ymjElf1ugTSyugeeLgDgqb0z5atJaqTZ5zc7UqKQQG9HlM7KIDUgTwUyagKjXMGq+2nWFLD
TZ30KudWmMMNKjp7GAHvNAgz35sZjE4P/Mq7g0Od+vQ7IcPOipdROt4xDXPv5raNeJiSai4S4Kba
dpP/vzvqBUZyLDpMdzhcbne/c9Hu/Zq106qvVky+GRfSf2OhAN0wNGqd73rVEm/1f/QjGW16KMxu
8/vjva8XF4wiFu3Q/sV5NDiCQWECgYEAvP3VTsBDTgb6EDqpwd8+j1H1Eue5O7zI9stAG7u+0rJv
FHUj6Awea5TYkcqBJrPMuI8dGh5PUwHrg6dWjTT5/R1X+RKK64h6tYuqqUA5FRoHcwfq9vTkOJV0
63/vJUp9Zm8KWynczQFhLWKGKcif/pQ8wXpkp8t+TJDm89bT8LkCgYEAsk2pFTflieVgoU13M2Ed
2WXrBjHp3kMseJvvBag125kAN+n6ZV47WDoyHDPSwSk0VE1PWeKjSvh3lLt2/vvA7cXkK1iH/zEq
nBkTBMiF36+hB8UPzckqzGUgE3j82X32N77XaBRnZl0lU/XQEdm4OOc3i2XYxV6jbih9vppxPfMC
gYBCobPM+hhAsFEF28jyI4Vo/lpLegtitmKcMHi/zmeu3V4wdkRckbk/8NCSRjVWsdmh0ENQbBNH
jsu8NQlc66qfxPK5TAJSnGG3FDDtT0lQ2UZ7FfWPcDPuhzMbvJVSLnsb3FZoYdAJL01VtQDcRnGy
Tg1FoaNPTX2P/R6QJdO/cQKBgDseqOuSJxe76HhTWSy+DMmik3TwY90AZORwv6Yeig0QBBSGDjJC
NmcglLDpNf46DVHOeHsTPJWFIRE9v0z4aJXuQaNlrWIeCUTMw5OYcVsjvr72xjCzfO9csHAEc8Ih
k9wT+RRXf5lfVRsrrBvfFsg3UiF0WZXHtWS3JEpopxelAoGARqI8Z9DbFwi2HWYE0+FYO0hbHQ7k
8ZEnBqxML0agJp4F9/6fZIhP4PjU/gN6Qdun7QYh1SsEfAu5cR3Qn4S4a6pYsPESNab4eRajWfYG
yV62wcd87wjy//HKNRWzkItyn57We7LhVxJ/cw3r0y5ZDYB1amSTm8VrdYmtuI9Y9Yc=
-----END RSA PRIVATE KEY-----" >> /root/.ssh/id_rsa

chmod 400 /root/.ssh/id_rsa


mkdir -p /root/.aws
echo "[default]
aws_access_key_id = AKIAIRSLJ66PIEQTK2RA
aws_secret_access_key = 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
region = ${region}" >> /root/.aws/config


echo "* soft nofile 102400
* hard nofile 204800" >> /etc/security/limits.conf

ulimit -n 102400

echo "*/2 * * * * bash /home/ec2-user/massival/autoscalesvr/remote/crond_forlinksvr.sh > /dev/null 2>&1" >> /var/spool/cron/root

service crond restart


########
## NGINX
########
yum install nginx -y
mkdir -p ${LOG_DIR}/nginx
\cp ${DIR}/nginx.conf /etc/nginx/nginx.conf
\cp ${DIR}/autoscalesvr.conf /etc/nginx/conf.d/autoscalesvr.conf
echo "bash ${DIR}/start.sh" >> /etc/rc.local

service nginx restart

mkdir -p ${LOG_DIR}/uwsgi

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
mkdir -p ${LOG_DIR}/ssdb
export PATH=$PATH:/usr/local/ssdb
#ssdb-server

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


#######
## MySQL
#######

mkdir -p /var/log/mysql
chmod -R 777 /var/log/mysql
chown -R mysql:mysql /var/log/mysql
/etc/init.d/mysqld restart

mysql -e "grant select on *.* to admin@'10.0.%' identified by '123456' "



mkdir -p ${ASSETS_DIR}
chown -R ec2-user:ec2-user ${ASSETS_DIR}

