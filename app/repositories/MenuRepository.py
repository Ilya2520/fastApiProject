# Standard Library
import uuid
from typing import Union

# Third Party
from fastapi import Depends, HTTPException

# Library
from app.database.database import (
    MenuModel,
    Session,
    get_db,
    get_submenu_count,
    get_submenu_dishes,
)
from app.models.models import Menu
from app.repositories.Repository import Repository
from app.repositories.SubmenuRepository import SubmenuRepository


class MenuRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Menu

    def create(
        self,
        menu: Menu,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
    ) -> dict:
        db_menu = MenuModel(title=menu.title, description=menu.description)
        self.session.add(db_menu)
        self.session.commit()
        self.session.refresh(db_menu)
        return {
            "id": db_menu.id,
            "title": db_menu.title,
            "description": db_menu.description,
            "submenu_count": 0,
            "dishes_count": 0,
        }

    def get(
        self,
        menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        db_menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == menu_id)
            .first()
        )
        submenus_count = get_submenu_count(self.session, menu_id)  # type: ignore
        submenus_with_dishes = get_submenu_dishes(self.session, menu_id)  # type: ignore

        submenu_info = [
            {
                "id": submenu.id,
                "title": submenu.title,
                "description": submenu.description,
                "dishes_count": submenu.dishes_count,
            }
            for submenu in submenus_with_dishes
        ]

        if db_menu is None:
            raise HTTPException(status_code=404, detail="menu not found")
        else:
            menu_info = {
                "id": menu_id,
                "title": db_menu.title,
                "description": db_menu.description,
                "submenus_count": submenus_count,
                "submenus": submenu_info,
                "dishes_count": sum(
                    submenu.dishes_count for submenu in submenus_with_dishes
                ),
            }
            return menu_info

    def get_all(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
    ):
        all_menus = self.session.query(MenuModel).all()
        menus_info = []
        for menu in all_menus:
            submenus_count = get_submenu_count(self.session, menu.id)
            submenus_with_dishes = get_submenu_dishes(self.session, menu.id)
            submenu_info = SubmenuRepository(session=self.session).get_all(  # type: ignore
                api_test_menu_id=menu.id
            )

            menus_info.append(
                {
                    "id": menu.id,
                    "title": menu.title,
                    "description": menu.description,
                    "submenus": submenu_info,
                    "submenus_count": submenus_count,
                    "dishes_count": sum(
                        submenu.dishes_count
                        for submenu in submenus_with_dishes
                    ),
                }
            )
        return menus_info

    def update(
        self,
        target_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
        menu: Menu,
    ):
        if target_menu_id is None:
            raise HTTPException(
                status_code=400, detail="Invalid target_menu_id"
            )
        db_menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == target_menu_id)
            .first()
        )
        if db_menu is not None:
            if menu and menu.title:
                db_menu.title = menu.title
            if menu and menu.description:
                db_menu.description = menu.description
            self.session.commit()
            self.session.refresh(db_menu)
            return MenuModel(
                id=str(db_menu.id),
                title=db_menu.title,
                description=db_menu.description,
            )
        else:
            raise HTTPException(status_code=404, detail="Menu not found")

    def delete(
        self,
        menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        db_menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == menu_id)
            .first()
        )
        if db_menu:
            for submenu in db_menu.submenus:
                self.session.delete(submenu)
            self.session.delete(db_menu)
            self.session.commit()
            return {"message": "successful"}
        return {"message": "error"}
