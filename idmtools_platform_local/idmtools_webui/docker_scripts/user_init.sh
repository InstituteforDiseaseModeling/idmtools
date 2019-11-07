#!/usr/bin/env bash
/init &
sleep 2
cd /app
npm install -g yarn
echo "Running '$@' as idmtools"
su idmtools -c "$@"
