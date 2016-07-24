
DIR=$(readlink -f $(dirname $0))

python ${DIR}/../aws_query.py get_autoscale | grep "i-" | while read line
do
	ip=`echo $line | awk '{print $2}'`
	bash ${DIR}/backup2master.sh $ip
	bash ${DIR}/rsync2linksvr.sh $ip
done

