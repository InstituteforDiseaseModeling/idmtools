#!/usr/bin/with-contenv sh

# This script launches the idmtools locald workers

exec /usr/local/bin/dramatiq  idmtools_platform_local.workers.brokers:redis_broker idmtools_platform_local.workers.run