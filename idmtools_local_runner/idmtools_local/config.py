import os
true_options = ['y', 't', 'true', 'yes', '1']

DATA_PATH = os.getenv("DATA_PATH", "/data")
SQLALCHEMY_ECHO = (os.getenv('SQLALCHEMY_ECHO', '0').lower() in true_options)
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', "postgresql+psycopg2://idmtools:idmtools@postgres/idmtools")

