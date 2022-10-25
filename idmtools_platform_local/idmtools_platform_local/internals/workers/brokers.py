"""idmtools local platform redis broker config/setup.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import dramatiq
from logging import getLogger
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend, StubBackend

logger = getLogger(__name__)

redis_broker = None
redis_backend: RedisBackend = None


def setup_broker(heartbeat_timeout=60):
    """Setup broker."""
    global redis_broker
    global redis_backend

    if os.getenv("UNIT_TESTS") == "1":
        redis_broker = StubBroker()
        redis_backend = StubBackend()
        redis_broker.add_middleware(Results(backend=redis_backend))
        dramatiq.set_broker(redis_broker)
    elif redis_broker is None:
        REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        REDIS_URL = os.environ.get("REDIS_URL", f"redis://{REDIS_HOST}:6379")
        logger.debug(f"Using Redis URL: {REDIS_URL}")
        redis_broker = RedisBroker(url=REDIS_URL, heartbeat_timeout=heartbeat_timeout)
        redis_backend = RedisBackend(url=REDIS_URL)
        redis_broker.add_middleware(Results(backend=redis_backend))
        dramatiq.set_broker(redis_broker)
    return redis_broker


def get_brokers(heartbeat_timeout=60):
    """Get our redis brokers."""
    setup_broker(heartbeat_timeout)
    return redis_broker, redis_backend


def close_brokers():
    """Close all our brokers."""
    global redis_broker
    global redis_backend
    if redis_broker:
        redis_broker.close()
        redis_broker = None
    if redis_backend:
        redis_backend = None
