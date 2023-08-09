# Standard Library
# Third Party
from fastapi import FastAPI


# Library
from app.database.database import Session as db_session
from app.database.database import clear_database
from app.services.RedisService import RedisService
from app.crud import app as crud

app = FastAPI()


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def clear_db_on_startup() -> None:
    with db_session() as db:
        clear_database(db)


clear_db_on_startup()


def clear_redis_on_startup() -> None:
    r = RedisService()
    r.redis.flushall()


clear_redis_on_startup()

app.include_router(crud)
