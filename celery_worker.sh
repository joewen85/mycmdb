#!/bin/bash
# Author: Joe wen
# Blog: https://www.joewen.net
# Time: 2021-01-04 22:00:54
# Name: celery_worker.sh
# Version: v1.0
# Description: This is a Script.
PROJECT_PATH="/data/apps/mycmdb"
CELERY_BIN="/root/.local/share/virtualenvs/mycmdb-K9LHJHx5/bin/celery"
CELERY_APP="cmdb"
#CELERYD_OPTS="--time-limit=300 --concurrency=4"
CELERYD_OPTS="--concurrency=4"
CELERYD_LOG_LEVEL="INFO"
CELERYD_LOG_FILE="/data/apps/mycmdb/log/celery_%n.log"
#CELERYD_LOG_FILE="/data/apps/mycmdb/log/celery_%n%I.log"
CELERYD_PID_FILE="/data/apps/mycmdb/%n.pid"
# 必须添加这个环境变量
export PYTHONOPTIMIZE=1

celery_start(){
  /root/.pyenv/shims/pipenv run ${CELERY_BIN} -A ${CELERY_APP} multi start w1 -E -l ${CELERYD_LOG_LEVEL} --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} ${CELERYD_OPTS}
}

celery_stop(){
  /root/.pyenv/shims/pipenv run ${CELERY_BIN} -A ${CELERY_APP} multi stop w1 -E -l ${CELERYD_LOG_LEVEL} --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} ${CELERYD_OPTS}
}
cd ${PROJECT_PATH}
case $1 in
    start)
    celery_start
    ;;
    stop)
    celery_stop
    ;;
    reload)
    celery_stop
    celery_start
    ;;
    *)
    echo "usage $0 [ start|stop|reload ]"
esac
