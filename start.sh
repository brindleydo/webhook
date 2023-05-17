#!/bin/bash

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, ex /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

cd "$SCRIPTPATH"
echo "Activating Python VirtualEnv"
source .env/bin/activate

echo "Starting Webhook Server"
python3 main.py
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]
	then echo -e "\033[1;32m\033[0m Webhook completed with exitcode \033[1;33m$EXIT_CODE\033[0m!"
	else echo -e "\033[1;31m\033[0m Webhook failed with exitcode \033[1;33m$EXIT_CODE\033[0m!"
fi

echo "Cleaning Up"
deactivate

exit $EXIT_CODE
