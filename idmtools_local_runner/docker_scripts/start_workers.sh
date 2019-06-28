#!/usr/bin/with-contenv sh

# This script launches the idmtools locald workers

exec /usr/local/bin/dramatiq  idmtools_local.brokers:redis_broker idmtools_local.run