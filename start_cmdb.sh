#!/bin/bash
# Author: Joe wen
# Blog: https://www.joewen.net
# Time: 2019-05-24 10:16:16
# Name: start_cmdb.sh
# Version: v1.0
# Description: This is a Script.

# Comments to support chkconfig on RedHat Linux
# chkconfig: 2345 64 36
# description: cmdb

### BEGIN INIT INFO
# Provides: cmdb
# Required-Start: $local_fs $network $remote_fs
# Should-Start: ypbind nscd ldap ntpd xntpd
# Required-Stop: $local_fs $network $remote_fs
# Default-Start:  2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: start and stop cmdb
# Description: cmdb
### END INIT INFO

path='/opt/mycmdb'
envexec="${path}/py3/bin/activate"

source ${envexec}
cd ${path}

case $1 in
	start)
	uwsgi --ini ${path}/uwsgi.ini
	;;
	reload)
	uwsgi --reload ${path}/uwsgi.pid
	;;
	stop)
	uwsgi --stop ${path}/uwsgi.pid
	;;
	*)
	echo -e "Usage $0 start|reload|stop"
	exit 3
	;;
esac

deactivate

exit $?
