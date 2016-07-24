domain=$1
user=$2
did=`date +%Y-%m-%d-%H:%M:%S`
DIR=$(readlink -f $(dirname $0))
aws route53 create-hosted-zone --name ${domain} --caller-reference $did --hosted-zone-config Comment="${user}-${did}" > ${DIR}/tmp/${domain}.tmp
cat ${DIR}/tmp/${domain}.tmp
zoneid=`cat ${DIR}/tmp/${domain}.tmp | grep hostedzone | grep -v 'amazon' | awk -F "hostedzone/" '{print $2}' | awk -F "\"" '{print $1}'`
sed "s/xxxdomainxxx/${domain}/g" ${DIR}/sample.json > ${DIR}/tmp/${domain}.json
aws route53 change-resource-record-sets --hosted-zone-id ${zoneid} --change-batch file://${DIR}/tmp/${domain}.json
