#!/usr/bin/env bash
# create directory so it is owned by user
mkdir -p ../data/redis-data ../data/postgres-data || true
# on linux, we need proper permissions. This just makes that easier so users don't have to remember
CURRENT_UID=$(id -u):$(id -g) docker-compose up -d