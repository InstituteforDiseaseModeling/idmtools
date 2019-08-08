import os

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend, StubBackend

redis_broker = None
redis_backend = None


def setup_broker():
    global redis_broker
    global redis_backend
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

    if os.getenv("UNIT_TESTS") == "1":
        redis_broker = StubBroker()
        redis_backend = StubBackend()
    else:
        redis_broker = RedisBroker(url=REDIS_URL)
        redis_backend = RedisBackend(url=REDIS_URL)
    redis_broker.add_middleware(Results(backend=redis_backend))
    dramatiq.set_broker(redis_broker)
    return redis_broker


redis_broker = setup_broker()
