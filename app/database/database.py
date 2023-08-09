# Standard Library
import os
import uuid

# Third Party
from sqlalchemy import Column, ForeignKey, Numeric, String, create_engine, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = 'db'
POSTGRES_PORT = '5432'
POSTGRES_DB = os.environ.get('POSTGRES_DB')

DATABASE_URL = (
    f'postgresql://{POSTGRES_USER}:'
    f'{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Base = declarative_base()
# engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
# Session = sessionmaker(bind=engine)
# session = Session()


class MenuModel(Base):  # type: ignore
    __tablename__ = 'menus'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title = Column(String)
    description = Column(String)
    submenus = relationship('SubmenuModel', back_populates='menu')


class SubmenuModel(Base):  # type: ignore
    __tablename__ = 'submenus'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title = Column(String, unique=True)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey('menus.id'))
    menu = relationship('MenuModel', back_populates='submenus')
    dishes = relationship('DishModel', back_populates='submenu')


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


Base.metadata.create_all(bind=engine)


def clear_database(session: Session):  # type: ignore
    session.query(DishModel).delete()  # type: ignore
    session.query(SubmenuModel).delete()  # type: ignore
    session.query(MenuModel).delete()  # type: ignore
    session.commit()  # type: ignore


def get_submenu_count(session: Session, menu_id: uuid.UUID):  # type: ignore
    return (
        session.query(func.count(SubmenuModel.id))  # type: ignore
        .filter(SubmenuModel.menu_id == menu_id)
        .scalar() or 0
    )


def get_submenu_dishes(session: Session, menu_id: uuid.UUID):  # type: ignore
    return (
        session.query(  # type: ignore
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
        .all()
    )


def format_price(x):
    return format(x, '.2f')


def get_submenu_dishes_count(session: Session, submenu_id: uuid.UUID):  # type: ignore
    return (
        session.query(func.count(DishModel.id))  # type: ignore
        .filter(DishModel.submenu_id == submenu_id)
        .scalar() or 0
    )


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
