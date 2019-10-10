#!/usr/bin/with-contenv sh

# This launches the workers that do all the actual run task work
exec s6-setuidgid idmtools /usr/local/bin/dramatiq idmtools_platform_local.workers.brokers:redis_broker idmtools_platform_local.workers.run --queues cpu --threads 1