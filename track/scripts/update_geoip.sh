mkdir -p /tmp/geoip
geoipupdate -f /root/massival/scripts/GeoIP.conf -d /tmp/geoip
#rsync -avz eudb:/tmp/geoip/ /tmp/geoip/
chmod -R 777 /tmp/

DIR=$(readlink -f $(dirname $0))

cat /root/.ssh/config | grep "^Host v3_.*m$" | while read line
do
    ip=`echo $line | awk '{print $2}'`
    echo $ip
    rsync -avz /tmp/geoip/ $ip:/tmp/
done
