#!/usr/bin/env bash
docker-compos build
docker-compose run linuxtst
docker-compose down