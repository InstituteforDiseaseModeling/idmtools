#!/usr/bin/with-contenv sh

# This script launches the idmtools local fast workers(copying files, creating sims, creating experiments)
exec s6-setuidgid idmtools /usr/local/bin/dramatiq idmtools_platform_local.internals.workers.run_broker:redis_broker idmtools_platform_local.internals.workers.run --processes 3 --threads 3 --queues default
