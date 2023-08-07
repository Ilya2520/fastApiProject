# Standard Library
import uuid
from typing import Union

# Third Party
from fastapi import Depends, HTTPException

# Library
from app.database.database import (
    MenuModel,
    Session,
    SubmenuModel,
    format_price,
    get_db,
    get_submenu_dishes_count,
)
from app.models.models import Submenu
from app.repositories.Repository import Repository


class SubmenuRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Submenu

    def get_all(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None] = None,
    ):
        menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == api_test_menu_id)
            .first()
        )
        if menu is None:
            return []
        submenu_info = []
        for submenu in menu.submenus:
            dishes_count = get_submenu_dishes_count(self.session, submenu.id)
            submenu_dishes = []
            for dish in submenu.dishes:
                submenu_dishes.append(
                    {
                        "id": dish.id,
                        "title": dish.title,
                        "description": dish.description,
                        "price": dish.price,
                    }
                )
            submenu_info.append(
                {
                    "id": submenu.id,
                    "title": submenu.title,
                    "description": submenu.description,
                    "dishes": submenu_dishes,
                    "dishes_count": dishes_count,
                }
            )
        return submenu_info

    def create(
        self,
        submenu: Submenu,
        menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
    ):
        nw_submenu = SubmenuModel(
            title=submenu.title, description=submenu.description
        )
        dishes_count = get_submenu_dishes_count(self.session, nw_submenu.id)
        db_menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == menu_id)
            .first()
        )
        if db_menu is None:
            return []
        db_menu.submenus.append(nw_submenu)
        self.session.add(nw_submenu)
        self.session.commit()
        return {
            "id": nw_submenu.id,
            "title": nw_submenu.title,
            "description": nw_submenu.description,
            "dishes_count": dishes_count,
        }

    def get(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == api_test_menu_id)
            .first()
        )
        for a in menu.submenus:
            if a.id == submenu_id:
                dishes_count = get_submenu_dishes_count(
                    self.session, submenu_id
                )
                submenu_info = {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "dishes_count": dishes_count,
                }
                dishes_info = [
                    {
                        "id": dish.id,
                        "title": dish.title,
                        "description": dish.description,
                        "price": format_price(dish.price),
                    }
                    for dish in a.dishes
                ]
                submenu_info["dishes"] = dishes_info
                return submenu_info
        raise HTTPException(status_code=404, detail="submenu not found")

    def update(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
        submenu: Submenu,
    ):
        menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == api_test_menu_id)
            .first()
        )
        if menu is not None:
            for a in menu.submenus:
                if a.id == submenu_id:
                    if submenu.title:
                        a.title = submenu.title
                    if submenu.description:
                        a.description = submenu.description
                    self.session.commit()
                    self.session.refresh(a)
                    return {
                        "id": a.id,
                        "title": a.title,
                        "description": a.description,
                    }
            raise HTTPException(status_code=404, detail="Submenu not found")
        raise HTTPException(status_code=404, detail="Menu not found")

    def delete(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        menu = (
            self.session.query(MenuModel)
            .filter(MenuModel.id == api_test_menu_id)
            .first()
        )
        for i, submenu in enumerate(menu.submenus):
            if submenu.id == submenu_id:
                for dish in submenu.dishes:
                    self.session.delete(dish)
                self.session.delete(submenu)
                self.session.commit()
                return {"message": "successful delete"}
        raise HTTPException(status_code=404, detail="submenu not found")
