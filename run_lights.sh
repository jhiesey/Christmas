#!/bin/sh
COMMAND="pypy /home/pi/Christmas/controller/rainbowController.py"
pgrep -f -x "$COMMAND" > /dev/null 2>&1 || $COMMAND
