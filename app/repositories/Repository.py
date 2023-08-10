# Standard Library

import uuid
from abc import abstractmethod

# Third Party
from fastapi import Depends
from pydantic import BaseModel

# Library
from app.database.database import Session, get_db


class Repository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session: Session = session

    @abstractmethod
    def create(
        self,
        item: BaseModel,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
    ) -> dict:
        pass

    @abstractmethod
    def get(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
        dish_id: uuid.UUID | None,
    ):
        pass

    @abstractmethod
    def get_all(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
    ):
        pass

    @abstractmethod
    def delete(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
        dish_id: uuid.UUID | None,
    ):
        pass

    @abstractmethod
    def update(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
        dish_id: uuid.UUID | None,
        item: BaseModel,
    ):
        pass
