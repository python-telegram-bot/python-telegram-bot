#!/bin/sh
clear
echo running
tput setaf 2;
echo docker run -it --workdir /home python-telegram-bot pipenv run python main.py
echo 
echo --------------------------------
echo  press CTRL + C to quit
echo --------------------------------
docker run -it --workdir /home python-telegram-bot pipenv run python main.py