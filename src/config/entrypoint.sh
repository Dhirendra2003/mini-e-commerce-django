#!/bin/bash

echo "Current directory:"
pwd

echo "Files in current directory:"
ls -al

APP_PORT=${PORT:-8000}
cd /app/

echo "Inside /app directory:"
pwd
ls -al


APP_PORT=${PORT:-8000}
cd /app/ 
gunicorn cfehome.wsgi:application --bind "0.0.0.0:${APP_PORT}"