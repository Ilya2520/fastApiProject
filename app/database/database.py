# Standard Library
import os
import uuid
from collections.abc import AsyncGenerator

# Third Party
from sqlalchemy import Column, ForeignKey, Numeric, String, func, delete
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = 'db'
POSTGRES_PORT = '5432'
POSTGRES_DB = os.environ.get('POSTGRES_DB')

DATABASE_URL = (
    f'postgresql+asyncpg://{POSTGRES_USER}:'
    f'{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)
#
# engine = create_engine(DATABASE_URL)
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()


# Base = declarative_base()
# engine = create_async_engine('postgresql+asyncpg://postgres:1234@localhost:5432/postgres')
# Session = sessionmaker(bind=engine)
# session = Session()
#
# DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"
#
#
# engine = create_async_engine(DATABASE_URL, echo=True)
# Base = declarative_base()
# async_session = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )
#
#
# DATABASE_URL = 'postgresql+asyncpg://postgres:1234@localhost:5432/postgres'
#
# if os.environ.get('TESTING'):
#     # Используйте SQLite для тестов
#     print("test....................................")
#     SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
#     engine = create_async_engine(
#         SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
#     )
# else:
# Используйте PostgreSQL для основной базы данных
engine = create_async_engine(DATABASE_URL, future=True)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True  # type: ignore
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class MenuModel(Base):  # type: ignore

    __tablename__ = 'menus'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title = Column(String)
    description = Column(String)
    submenus = relationship('SubmenuModel', back_populates='menu', lazy='selectin')


class SubmenuModel(Base):  # type: ignore
    __tablename__ = 'submenus'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title = Column(String, unique=True)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'))
    menu = relationship('MenuModel', back_populates='submenus')
    dishes = relationship('DishModel', back_populates='submenu', lazy='selectin')


class DishModel(Base):  # type: ignore
    __tablename__ = 'dishes'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title = Column(String, unique=True)
    description = Column(String)
    price = Column(Numeric())
    submenu_id = Column(UUID(as_uuid=True), ForeignKey('submenus.id'))
    submenu = relationship('SubmenuModel', back_populates='dishes')


async def clear_database():  # type: ignore
    async with AsyncSession(bind=engine) as session:
        await session.execute(delete(DishModel))
        await session.execute(delete(SubmenuModel))
        await session.execute(delete(MenuModel))
        await session.commit()


async def get_submenu_count(session: AsyncSession, menu_id: uuid.UUID):
    result = await session.execute(
        select(func.count(SubmenuModel.id))
        .filter(SubmenuModel.menu_id == menu_id)
    )
    return result.scalar() or 0


async def get_submenu_dishes(session: AsyncSession, menu_id: uuid.UUID):
    result = await session.execute(
        select(
            SubmenuModel.id,
            SubmenuModel.title,
            SubmenuModel.description,
            func.count(DishModel.id).label('dishes_count'),
        )
        .outerjoin(DishModel, SubmenuModel.id == DishModel.submenu_id)
        .filter(SubmenuModel.menu_id == menu_id)
        .group_by(
            SubmenuModel.id, SubmenuModel.title, SubmenuModel.description
        )
    )
    return result.all()


def format_price(x):
    return format(x, '.2f')


async def get_submenu_dishes_count(session: AsyncSession, submenu_id: uuid.UUID):
    result = await session.scalar(
        select(func.count(DishModel.id))
        .filter(DishModel.submenu_id == submenu_id)
    )
    return result or 0


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
