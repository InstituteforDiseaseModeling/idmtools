import json
import os
from collections import OrderedDict
from enum import Enum

import dramatiq
from logging import getLogger
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.encoder import MessageData
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend, StubBackend

logger = getLogger(__name__)

redis_broker = None
redis_backend: RedisBackend = None


def setup_broker(heartbeat_timeout=60):
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
        dramatiq.set_encoder(LocalPlatformDRJSONEncoder())
    return redis_broker


def get_brokers(heartbeat_timeout=60):
    setup_broker(heartbeat_timeout)
    return redis_broker, redis_backend


def close_brokers():
    global redis_broker
    global redis_backend
    if redis_broker:
        redis_broker.close()
        redis_broker = None
    if redis_backend:
        redis_backend = None


class LocalPlatformJSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, OrderedDict):
            return json.JSONEncoder.encode(self, dict(obj))
        return json.JSONEncoder.default(self, obj)


class LocalPlatformDRJSONEncoder(dramatiq.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = LocalPlatformJSONEncoder()

    def encode(self, obj):
        return self.encoder.default(obj)
    
    def decode(self, data: bytes) -> MessageData:
        return super(LocalPlatformDRJSONEncoder, self).decode(data)
