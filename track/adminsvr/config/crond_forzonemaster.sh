
DIR=$(readlink -f $(dirname $0))

cat /root/.ssh/config | grep "^Host v3_.*m$" | while read line
do
	ip=`echo $line | awk '{print $2}'`
    	echo $ip
	bash ${DIR}/backup2adminsvr.sh $ip
	bash ${DIR}/rsync2zonemaster.sh $ip
done

