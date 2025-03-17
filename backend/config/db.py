from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os

def get_engine():
    url = URL.create(
        drivername="postgresql",
        username=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        database=os.environ["DATABASE_NAME"],
        password=os.environ["DATABASE_PASSWORD"]
    )
    return create_engine(url)
