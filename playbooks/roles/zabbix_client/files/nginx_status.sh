#!/bin/bash
#check nginx status
# export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
. /etc/profile
ping() {
  /sbin/pidof nginx | wc -l
}
active() {
  curl http://127.0.0.1/status 2>/dev/null |sed -n '1p'|awk '{print $NF}'
}
accepts() {
  curl http://127.0.0.1/status 2>/dev/null |sed -n '3p'|awk '{print $1}'
}
handled(){
  curl http://127.0.0.1/status 2>/dev/null |sed -n '3p'|awk '{print $2}'
}
requests(){
  curl http://127.0.0.1/status 2>/dev/null |sed -n '3p'|awk '{print $3}'
}
reading(){
  curl http://127.0.0.1/status 2>/dev/null |sed -n '4p'|awk '{print $2}'
}
writing(){
  curl http://127.0.0.1/status 2>/dev/null |sed -n '4p'|awk '{print $4}'
}
waiting(){
  curl http://127.0.0.1/status 2>/dev/null |sed -n '4p'|awk '{print $6}'
}
case $1 in
  ping)
  ping
  ;;
  active)
  active
  ;;
  accepts)
  accepts
  ;;
  handled)
  handled
  ;;
  requests)
  requests
  ;;
  reading)
  reading
  ;;
  writing)
  writing
  ;;
  waiting)
  waiting
  ;;
esac
