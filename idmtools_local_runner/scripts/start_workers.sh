#!/usr/bin/with-contenv sh
exec /usr/local/bin/dramatiq --verbose idmtools_local.brokers:redis_broker idmtools_local.run