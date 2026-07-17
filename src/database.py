import platform
import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .models import Base

load_dotenv()

we_inside_docker_container = os.path.exists('/.dockerenv')
print('we inside Docker container: ', we_inside_docker_container)

DB_USER=os.getenv('POSTGRES_USER')
DB_PASS=os.getenv('POSTGRES_PASSWORD')
DB_PORT=os.getenv('POSTGRES_PORT')
DB_NAME=os.getenv('POSTGRES_DB')
# on local machine use forwarded port from localhost to Docker container localhost:5432->pgdatabase:5432
# inside Docker container use container name pgdatabase:5432
DB_HOST='pgdatabase' if we_inside_docker_container else 'localhost'

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db  # yield, not return. we need to run db.commit() after endpoint finish its work
            await db.commit()  # bad practice? we call db.commit for all db queries, including select
        except Exception:
            await db.rollback()
            raise

SessionDep = Annotated[AsyncSession, Depends(get_db)]

# create tables if not exist
async def create_db_tables():
    async with engine.begin() as conn:
        # run_sync passes the connection to create_all automatically
        await conn.run_sync(Base.metadata.create_all)




