#!/bin/bash


consul_pid=`ps -A | grep 'consul agent -dev -advertise 127.0.0.1' | grep -v grep | awk '{print $1}'`
if [ "$consul_pid" != "" ] ; then
	kill $consul_pid
fi
