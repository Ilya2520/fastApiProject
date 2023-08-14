# Standard Library
import uuid
from abc import abstractmethod

# Third Party
from fastapi import Depends
from pydantic import BaseModel

# Library
from app.database.database import AsyncSession as Session
from app.database.database import get_session as get_db


class Repository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session: Session = session

    @abstractmethod
    async def create(
        self,
        item: BaseModel,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
    ) -> dict:
        pass

    @abstractmethod
    async def get(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
        dish_id: uuid.UUID | None,
    ):
        pass

    @abstractmethod
    async def get_all(
        self,
        api_test_menu_id: uuid.UUID | None,
        submenu_id: uuid.UUID | None,
    ):
        pass
    #
    # def create(
    #         self,
    #         model: Model,
    #         menu_id: uuid.UUID | None,
    #         submenu_id: uuid.UUID | None,
    # ):
    #     if menu_id is None:
    #         db_item = MenuModel(title=model.title, description=model.description)
    #         db_item= Menu.from_orm(db_item)
    #     elif submenu_id is None:
    #         db_menu = (
    #             self.session.query(MenuModel)
    #             .filter(MenuModel.id == menu_id)
    #             .first()
    #         )
    #         if db_menu is None:
    #             return []
    #         db_item = SubmenuModel(title=model.title, description=model.description)
    #         db_menu.submenus.append(db_item)
    #     else:
    #         db_item = DishModel(title=model.title, description=model.description)
    #         submenu = (
    #             self.session.query(SubmenuModel)
    #             .filter(
    #                 SubmenuModel.id == submenu_id and SubmenuModel.menu_id == menu_id
    #             )
    #             .first()
    #         )
    #         if submenu is None:
    #             return []
    #         submenu.dishes.append(db_item)
    #     self.session.add(db_item)
    #     self.session.commit()
    #     self.session.refresh(db_item)
    #     return db_item

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
