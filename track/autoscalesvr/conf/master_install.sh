#!/bin/bash
yum install unzip expect nc git make automake gcc gcc-c++ kernel-devel python python-devel mysql-server mysql MySQL-python mysql-devel -y 
pip install awscli uwsgi virtualenv supervisor sqlalchemy geoip2 PyCrypto pyyaml redis requests flask flask-sqlalchemy mysql-python raven blinker init mako pymysql ujson pywurfl newrelic
ln -s /usr/local/bin/uwsgi /usr/bin/uwsgi
ln -s /usr/local/bin/newrelic-admin /usr/bin/newrelic-admin

########
## NGINX
########
rpm -ivh http://nginx.org/packages/centos/6/noarch/RPMS/nginx-release-centos-6-0.el6.ngx.noarch.rpm
yum install nginx -y
\cp nginx.conf /etc/nginx/nginx.conf
\cp default.conf /etc/nginx/conf.d/default.conf
\cp querysvr.conf /etc/nginx/conf.d/querysvr.conf

########
## TIME
########
\cp /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime
echo 'ZONE="Asia/Hong_Kong"
UTC=false
ARC=false' > /etc/sysconfig/clock
echo "StrictHostKeyChecking no
 UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config


########
## SSH
########
echo "-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQEA2BuIFjYCxcR4S225Y0BGSEeCqX9EE116ibcmHnTVoUJocJwK
b+oCpMTj/CN1w42kFlGqFSWZRZPOSJZYbWWl3JgBXgqTD5LPTmfQkkxUuat0z3nV
rWzNHrj3RJhNJ4p2PRMbF0O9CFGgSI55eg96Te3NAN0uQD7GsmOIARWlwkU2edi9
PggEvPW6/AoOdulxwk3i5OuPzwqNnUE0QFHvpJRSKduH2GLRFay0LLSDhPD8eCXQ
oneUVKBo26sALneWThKtbhMQwnnReBRmm1OXq8gfPadnyW8xriQcpr2n8wx/EAhR
hEBlhfZpUXEL37Q41/1eoeuXltVHaGjWVmqOVQIBIwKCAQBo9238KNzGdV8AELkh
lD9k74ibeFRD65NKNGL42amXeAbXnD+VcamDOw+mWl3FYg3e9Hcu1795kO8qkirz
TqEEvtwXu/5JZJCTzAY4bjfH5ZCCB/oSaAvbuO0hUUoL5CrNNSpqYrrmyI+uNpLG
Qgg0etFJkACFmtWJ2JKELxX/RUud76ZoQVAB1YdlbSb/RF3DzDOnUXejguht80dk
1RVxrd++VeteWW8lhE0iWJJPtX5pe2S9EdMu2whdGAYVWBx7uS6H2KUNoP6FgAso
eB8nU+2LMzzfhPy8tZMwqRh/hiV3OssHwP5uAVDvRjRgR7wMRmE8q7RKIF/h1/n0
zv0PAoGBAPd/wDvrvlytqJyhNOEv/J57pfuLKUeLTWpe557tWtM27WuZnxfoBpep
+mkewHzRTJsdYFYTz8ij5UA8hvQGb+BTsZsq82slW/wlcqmRFrv7R/RFv2nVlV7T
0qJht9u4lJdVjr25P4Y6aSvem6kl5onZsnDrgz4jBxA6Vs+6s5O3AoGBAN+HwbI/
aNYppI8gmhk5YBI7EowQVsprkYDykeQ4EzuSqlYmfHxMOq7xR44hmAamH6hjfCOf
+5FfUo/feh2/2dWwXEkNUo4IliOpMLUgVJuMtUHoYGKCBEL7cjwsIiFSCV5blx73
Rlr/qKXgkCQRsnchQY7uNARiuL0RzdbQ36ZTAoGAP6SB44XDPGcrW3npBrSRapTS
6OlFIQaQP+yEs9aiU5HIBbnJ0vKFWjMF4IRAIBiQCqEnZpdhUNmv+pM4pSY6Bnvr
13Fxyxg8OYX46cY5C8RFs9drvCD6hhk2KcFbKd8Bo0Hi4FQ06ABkL9ooBux9HCIJ
UDyPdmDHTVDUfo8YO+0CgYAMxe3Pq9oa3c7jm3aFGTiwlalJ1QxGFMZ8ZaHvyLCk
UYYTjSuvVNAnQPzGSxAAYUOjOOKFsV7VG2PNtP+p7bStIAVGAMLji3ZLLj1MLbux
Hfu6n5B6qFgD09qkWksX2M1V2VkXtlvKr4X62aHWLOWgaEzjmJVCFEUSHkZGyhto
lwKBgQDDMqEeZPYDf9kHV+FEPmK6cha5OYqq5VMPYRlFdHrpg9//kYqqHX/PlVAF
OHGAqT1tRVazgO0m/M4XwedniiOA/XmLxBAlK5vQ+7kku3wKb92fQfGg3KYuR1Zn
EAztCmofTO9mvOyY6PUvVi2I0pzhFMmd0HLNh4E0ZLcYRfCtFQ==
-----END RSA PRIVATE KEY-----" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
mkdir /root/.aws
echo '[default]
aws_access_key_id = AKIAIRSLJ66PIEQTK2RA
aws_secret_access_key = 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
region = us-east-1' > /root/.aws/config

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


mkdir /var/log/uwsgi

sed -i "/requiretty/d" /etc/sudoers

mkdir /var/log/mysql
chmod 777 /var/log/mysql



cd /root/massival/autoscalesvr/conf/
./run_autos_svr.sh
service nginx restart
