#!/usr/bin/with-contenv python
# we name this .sh so that docker windows doesn't
# pess with our EOLs
import os
import time
import socket

from sqlalchemy import create_engine
from idmtools_platform_local.config import SQLALCHEMY_ECHO
from idmtools_platform_local.internals.data import Base
from idmtools_platform_local.internals.workers.database import default_url

while True:
    try:
        url = os.getenv('SQLALCHEMY_DATABASE_URI', default_url)
        print(f"Initializing db")
        engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI', url), echo=SQLALCHEMY_ECHO, pool_size=2)
        # import models
        from idmtools_platform_local.internals.data.job_status import JobStatus

        Base.metadata.create_all(engine)
        print("Database Initialized")
        break
    except (ConnectionError, ConnectionRefusedError, LookupError, ConnectionRefusedError, ConnectionAbortedError):
        print("It appears the database is no ready. Trying again shortly")
        time.sleep(0.25)
    except Exception as e:
        print("Error: ")
        print(str(e))
        break
