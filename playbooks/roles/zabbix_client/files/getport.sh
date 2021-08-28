#!/bin/bash
grep "^Port" /etc/ssh/sshd_config |awk '{print $2}'
