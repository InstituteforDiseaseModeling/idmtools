#!/usr/bin/with-contenv sh

# This launches the workers that do all the actual gpu run task work
exec s6-setuidgid idmtools /usr/local/bin/dramatiq idmtools_platform_local.workers.brokers:redis_broker idmtools_platform_local.workers.run --processes 1 --threads 1 --queues gpu