#!/bin/bash
cd /home/karun777/futuresky
source discord-bot-env/bin/activate
export $(cat .env | xargs)
python3 bot/bot.py
