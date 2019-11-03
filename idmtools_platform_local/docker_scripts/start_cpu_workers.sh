#!/usr/bin/with-contenv sh

echo
# This launches the workers that do all the actual run task work
exec s6-setuidgid idmtools /usr/local/bin/dramatiq idmtools_platform_local.internals.workers.run_broker:redis_broker idmtools_platform_local.internals.workers.run --queues cpu --threads 1