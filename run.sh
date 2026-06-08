#!/bin/bash

source .venv/bin/activate

# NOTE ngrok will run in background, kill it with pkill ngrok
ngrok http --url=https://undeciphered-jasiah-biscuitlike.ngrok-free.dev 8000 --log=stdout > /dev/null &

python manage.py runserver
