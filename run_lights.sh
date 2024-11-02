#!/bin/sh

cd /home/jhiesey/Christmas

COMMAND="pypy3 /home/jhiesey/Christmas/controller/fallController.py"
pgrep -f -x "$COMMAND" > /dev/null 2>&1 || $COMMAND &

WEBCOMMAND="node /home/jhiesey/Christmas/web/index.js"
pgrep -f -x "$WEBCOMMAND" > /dev/null 2>&1 || $WEBCOMMAND &
