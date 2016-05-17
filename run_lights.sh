#!/bin/sh

cd /home/pi/Christmas

COMMAND="pypy /home/pi/Christmas/controller/rainbowController.py"
pgrep -f -x "$COMMAND" > /dev/null 2>&1 || $COMMAND &

WEBCOMMAND="nodejs /home/pi/Christmas/web/index.js"
pgrep -f -x "$WEBCOMMAND" > /dev/null 2>&1 || $WEBCOMMAND &
