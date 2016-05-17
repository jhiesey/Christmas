#!/bin/sh

cd /home/pi/Christmas/controller

COMMAND="pypy /home/pi/Christmas/controller/rainbowController.py"
pgrep -f -x "$COMMAND" > /dev/null 2>&1 || $COMMAND &


WEBCOMMAND="node /home/pi/Christmas/web/index.js"
pgrep -f -x "$WEBCOMMAND" > /dev/null 2>&1 || $WEBCOMMAND &
