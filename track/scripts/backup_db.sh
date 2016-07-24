cur_date=`date --date="-0 hour" +%Y%m%d%H`
mysqldump -h10.0.0.178 -uadmin -p123456 massival > /root/season/mysql_backup/massival_${cur_date}.sql
