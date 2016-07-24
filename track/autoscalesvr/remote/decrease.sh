#!/bin/bash

echo "--------------------------------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------------------------------"
date

BALANCER_NAME="alpha-massival"
DIR=$(readlink -f $(dirname $0))

magicnum=1

rm -rf /root/.ssh/known_hosts
LOCK=/tmp/decreaserunlockfile
[ -f $LOCK ] && exit

touch $LOCK
    task=`python ${DIR}/../aws_query.py get_autoscale`
    code=$?
    if [ $code != 0 ]
    then
        echo "season get_autoscale error"
        rm -rf $LOCK
        exit
    fi

    num=`python ${DIR}/../aws_query.py get_autoscale | wc -l`
    echo "$num autoscale instances"
    if [[ $num < ${magicnum} || $num == ${magicnum} ]]
    then
        echo "season instances enough"
        rm -rf $LOCK
        exit
    fi

    instance_str=`python ${DIR}/../aws_query.py get_autoscale | head -1`
    instanceid=`echo $instance_str | awk '{print $1}'`
    ipaddr=`echo $instance_str | awk '{print $2}'`

    echo "season deregister instance" $instanceid $ipaddr

    aws elb deregister-instances-from-load-balancer --load-balancer-name ${BALANCER_NAME} --instances ${instanceid}
    sleep 5
    bash ${DIR}/backup2master.sh ${ipaddr}
    scp ${DIR}/bak.sh ${ipaddr}:/tmp/
    ssh ${ipaddr} "sudo bash /tmp/bak.sh"
    sleep 5

    echo "season terminate instance" $instanceid $ipaddr

    aws autoscaling terminate-instance-in-auto-scaling-group --instance-id ${instanceid} --should-decrement-desired-capacity    


rm -rf $LOCK
