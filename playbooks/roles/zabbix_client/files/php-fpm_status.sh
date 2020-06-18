#!/bin/bash
#check php-fpm status
ping(){
  /sbin/pidof php-fpm|wc -l
}
start_since(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==4{print $3}'
}
accepted_conn(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==5{print $3}'
}
listen_queue(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==6{print $3}'
}
max_listen_queue(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==7{print $4}'
}
listen_queue_len(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==8{print $4}'
}
idle_processes(){
  /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==9{print $3}'
}
 active_processes(){
   /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==10{print $3}'
 }
 total_processes(){
   /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==11{print $3}'
 }
 max_active_processes(){
   /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==12{print $4}'
 }
 max_children_reached(){
   /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==13{print $4}'
 }
 slow_requests(){
   /usr/local/curl/bin/curl http://127.0.0.1/php-fpm_status 2>/dev/null |awk 'NR==14{print $3}'
 }
case $1 in
  ping)
  ping
  ;;
  start_since)
  start_since
  ;;
  accepted_conn)
  accepted_conn
  ;;
  listen_queue)
  listen_queue
  ;;
  max_listen_queue)
  max_listen_queue
  ;;
  listen_queue_len)
  listen_queue_len
  ;;
  idle_processes)
  idle_processes
  ;;
  active_processes)
  active_processes
  ;;
  total_processes)
  total_processes
  ;;
  max_active_processes)
  max_active_processes
  ;;
  max_children_reached)
  max_children_reached
  ;;
  slow_requests)
  slow_requests
  ;;
esac
