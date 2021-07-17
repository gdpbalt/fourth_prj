#!/bin/sh
#
#
RUN=control_update.sh

if ! /usr/bin/pgrep -al -f $RUN > /dev/null 2>/dev/null
then
	echo "Starting process"
	date

	/home/ubuntu/control/bin/$RUN

	echo "Stopping process"
	date
fi

