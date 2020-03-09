#!/bin/bash
source /etc/profile
GetDbInf(){
	db_host=$(awk -F":" '{print $2}' /etc/passwd-yunzhong)
	db_username=$(awk -F":" '{print $3}' /etc/passwd-yunzhong)
	db_password=$(awk -F":" '{print $4}' /etc/passwd-yunzhong)
}
useradd -M -s /sbin/nologin zabbix
cd /tmp
ZBCONF='/usr/local/zabbix/etc/zabbix_agentd.conf'
zabbixver='4.0.0'
tar zxf zabbix-$zabbixver.tar.gz
cd zabbix-$zabbixver
./configure --prefix=/usr/local/zabbix --enable-agent
make && make install
cd ..
rm -rf zabbix-$zabbixver
rm -rf zabbix-$zabbixver.tar.gz
sed -i 's/^# StartAgents=.*/StartAgents=0/' $ZBCONF
sed -i "s/^Hostname=.*/#Hostname=$hn/" $ZBCONF
sed -i 's/^# RefreshActiveChecks=.*/RefreshActiveChecks=60/' $ZBCONF
sed -i 's/^# BufferSize=.*/BufferSize=200/' $ZBCONF
sed -i "s/^# HostnameItem=system.hostname/HostnameItem=system.hostname/" $ZBCONF
touch /tmp/mounts.tmp
chown zabbix:zabbix /tmp/mounts.tmp
chmod +w /etc/sudoers
sed -i '/^Defaults\s\+requiretty/s/^/#/' /etc/sudoers
grep -q '^zabbix ALL=(ALL).*blockdev' /etc/sudoers || echo 'zabbix ALL=(ALL)       NOPASSWD: /sbin/blockdev' >> /etc/sudoers
chmod 440 /etc/sudoers
\cp /usr/local/zabbix/etc/zabbix_agentd /etc/init.d/
chmod +x /etc/init.d/zabbix_agentd
phpbinary=`find / -type f -name "php"|grep "/bin/php"`
for phprun in ${phpbinary}
do
        ver=$($phprun -v|grep "^PHP"|cut -d' ' -f2|awk -F"." '{print $1 $2}')
        if [ ${ver} -eq 56 ];then
                phpbin=${phprun}
                break
        fi
done
sed -i "s@/usr/local/php/bin/php@$phpbin@" /usr/local/zabbix/etc/get_mysql_stats_wrapper.sh
if [ -d /www/server ];then
	GetDbInf
	if [ -f /www/server/panel/vhost/nginx/phpfpm_status.conf ];then
		sed -i 's/nginx_status/status/' /www/server/panel/vhost/nginx/phpfpm_status.conf
		sed -i 's/phpfpm_56_status/php-fpm_status/' /www/server/panel/vhost/nginx/phpfpm_status.conf
		sed -i 's/^\(pm.status_path =\).*/\1 \/php-fpm_status/' /www/server/php/56/etc/php-fpm.conf
		sed -i "s/^\(\$mysql_user = \).*/\1'${db_username}';/" /usr/local/zabbix/etc/ss_get_mysql_stats.php
		sed -i "s/^\(\$mysql_pass = \).*/\1'${db_password}';/" /usr/local/zabbix/etc/ss_get_mysql_stats.php
		sed -i 's$/usr/local/mtr/sbin/mtr$/usr/sbin/mtr$' /usr/local/zabbix/etc/mtr_check.sh
		sed -i "s/^HOST=localhost/HOST='${db_host}'/" /usr/local/zabbix/etc/get_mysql_stats_wrapper.sh

	else
		echo "status.conf file not exist"
	fi
elif [ -d /www/wdlinux ];then
	GetDbInf
	if [ -f /www/wdlinux/phps/56/etc/php-fpm.conf ];then
	echo "pm.status_path = /php-fpm_status" >> /www/wdlinux/phps/56/etc/php-fpm.conf
	listen=$(grep "listen = /tmp/php-56-cgi.sock" /www/wdlinux/phps/56/etc/php-fpm.conf|awk '{print $3}')
	/www/wdlinux/phps/56/bin/php-fpm reload
	fi
	if [ -d /www/wdlinux/nginx/conf/vhost ];then
		curl -L https://downloads.yunzshop.com/status.conf -o /www/wdlinux/nginx/conf/vhost/status.conf
		sed -i "s/\(fastcgi_pass\).*/\1 unix:$listen;/" /www/wdlinux/nginx/conf/vhost/status.conf
		/etc/init.d/nginxd reload
	fi
	sed -i "s/^\(\$mysql_user = \).*/\1'${db_username}';/" /usr/local/zabbix/etc/ss_get_mysql_stats.php
                sed -i "s/^\(\$mysql_pass = \).*/\1'${db_password}';/" /usr/local/zabbix/etc/ss_get_mysql_stats.php
                sed -i 's$/usr/local/mtr/sbin/mtr$/usr/sbin/mtr$' /usr/local/zabbix/etc/mtr_check.sh
                sed -i "s/^HOST=localhost/HOST='${db_host}'/" /usr/local/zabbix/etc/get_mysql_stats_wrapper.sh

fi
if [ ! -f /usr/sbin/mtr ];then
	yum install -y mtr
fi
chkconfig --add zabbix_agentd
chkconfig zabbix_agentd on
chmod 644 /etc/ssh/sshd_config
