#!/usr/bin/env bash
# create directory so it is owned by user
mkdir -p ../data/redis-data || true
# ensure our network always exists
docker network create idmtools_network || true
# on linux, we need proper permissions. This just makes that easier so users don't have to remember
CURRENT_UID=$(id -u):$(id -g) docker-compose up -d