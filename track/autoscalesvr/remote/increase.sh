#!/bin/bash

echo "--------------------------------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------------------------------"
date

instanceid=$1
ipaddr=$2
DIR=$(readlink -f $(dirname $0))

rm -rf /root/.ssh/known_hosts

if  [ ! -n "$ipaddr" ] 
then
  echo "NO ipaddress found"
else

#  cat ${DIR}/instance_ids | grep ${instanceid} || {
#    echo "${instanceid}  ${ipaddr}" >> ${DIR}/instance_ids
#    aws elb deregister-instances-from-load-balancer --load-balancer-name massival --instances ${instanceid}
    sleep 10
    STT=1
    while [ $STT != 0 ]
    do
        sleep 5
        nc -z -w 2 $ipaddr 22
        STT=$?
    done

  aws ec2 describe-instance-attribute --instance-id  ${instanceid} --attribute sriovNetSupport | grep "simple"
  enhanst=$?
  if [ $enhanst != 0 ]
  then

    aws ec2 stop-instances --instance-ids ${instanceid}
    sleep 20
    STT=1
    while [ $STT != 0 ]
    do
        aws ec2 describe-instances --instance-ids ${instanceid} | grep terminated
        ttid=$?
        if [ $ttid == 0 ]
        then
            exit
        fi
        aws ec2 modify-instance-attribute --instance-id ${instanceid} --sriov-net-support simple
        STT=$?
        sleep 5
    done
    aws ec2 start-instances --instance-ids ${instanceid} > ${DIR}/tmp/${instanceid}
    cat ${DIR}/tmp/${instanceid} | grep "Instance does not have a volume attached at root\|is not in a state from which it can be started"
    sstopid=$?
    if [ $sstopid == 0 ]
    then
        aws autoscaling terminate-instance-in-auto-scaling-group --instance-id ${instanceid} --no-should-decrement-desired-capacity
        exit
    fi
    sleep 40
    STT=1
    while [ $STT != 0 ]
    do
        aws ec2 describe-instances --instance-ids ${instanceid} | grep terminated
        ttid=$?
        if [ $ttid == 0 ]
        then
            exit
        fi
        echo "Please wait 10 seconds to test the SSH connection..."
        sleep 10
        nc -z -w 2 $ipaddr 22
        STT=$?
    done
  fi
    rsync -av /home/ec2-user/massival ec2-user@${ipaddr}:/home/ec2-user/
    expect ${DIR}/sudo.exp $ipaddr
    sleep 2
     bash ${DIR}/rsync2linksvr.sh ${ipaddr}
#    aws elb register-instances-with-load-balancer --load-balancer-name massival --instances ${instanceid}
#  }
fi

