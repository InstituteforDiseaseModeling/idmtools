#!/usr/bin/with-contenv sh

# This script launches the idmtools local fast workers(copying files, creating sims, creating experiments)
exec s6-setuidgid idmtools /usr/local/bin/dramatiq --processes 2 idmtools_platform_local.workers.brokers:redis_broker idmtools_platform_local.workers.run --queues default
