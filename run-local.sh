#!/bin/sh
clear
echo running
tput setaf 2;
echo pipenv run python main.py
echo 
echo --------------------------------
echo  press CTRL + C to quit
echo --------------------------------
cd bot
pipenv run python main.py