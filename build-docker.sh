#!/bin/sh
docker build -t python-telegram-bot -f Dockerfile .
clear
echo --------------------------------
echo  python-telegram-bot 
echo  build finished
echo --------------------------------
echo .
echo  to run container use the following command:
tput setaf 2
echo docker run -it --workdir /home python-telegram-bot pipenv run python main.py
echo 
echo --------------------------------
echo  press CTRL + C to quit
echo --------------------------------