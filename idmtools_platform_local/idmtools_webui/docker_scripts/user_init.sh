#!/usr/bin/env bash
/init &
sleep 2
cd /app
[ -d "/app/build" ] && rm -rf /app/build
npm install -g yarn
echo "Running '$@' as idmtools"
su idmtools -c "$@"
