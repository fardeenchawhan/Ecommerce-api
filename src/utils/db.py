from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.utils.settings import settings

engine=create_engine(settings.DB_CONNECTION)

SessionLocal=sessionmaker(autocommit=False,autoflash=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()