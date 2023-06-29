#!/bin/sh

fuser -k 7998/tcp
echo "Server stopped, retrieving latest version from GitHub"
git pull -f
echo "Latest version downloaded, starting server ..."
nohup uvicorn main:app --host 0.0.0.0 --port 7998 &
