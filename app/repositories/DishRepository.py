# Standard Library
import uuid
from typing import Union

# Third Party
from fastapi import Depends, HTTPException

# Library
from app.database.database import (
    DishModel,
    Session,
    SubmenuModel,
    format_price,
    get_db,
)
from app.models.models import Dish
from app.repositories.Repository import Repository


class DishRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Dish

    def get_all(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
    ):
        menu = (
            self.session.query(SubmenuModel)
            .filter(
                SubmenuModel.id == submenu_id
                and SubmenuModel.menu_id == api_test_menu_id
            )
            .first()
        )
        if menu is None:
            return []
        dishes_info = []
        for dish in menu.dishes:
            dishes_info.append(
                {
                    "id": dish.id,
                    "title": dish.title,
                    "description": dish.description,
                    "price": format_price(dish.price),
                }
            )
        return dishes_info

    def create(
        self,
        dish: Dish,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
    ):
        nw_dish = DishModel(
            title=dish.title, description=dish.description, price=dish.price
        )
        submenu = (
            self.session.query(SubmenuModel)
            .filter(
                SubmenuModel.id == submenu_id
                and SubmenuModel.menu_id == api_test_menu_id
            )
            .first()
        )
        if submenu is None:
            raise HTTPException(status_code=404, detail="Submenu not found")
        submenu.dishes.append(nw_dish)
        self.session.add(nw_dish)
        self.session.commit()
        return {
            "id": nw_dish.id,
            "title": nw_dish.title,
            "description": nw_dish.description,
            "price": format_price(nw_dish.price),
        }

    def get(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        submenu = (
            self.session.query(SubmenuModel)
            .filter(
                SubmenuModel.id == submenu_id
                and SubmenuModel.menu_id == api_test_menu_id
            )
            .first()
        )
        for a in submenu.dishes:
            if a.id == dish_id:
                return {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "price": format_price(a.price),
                }
        raise HTTPException(status_code=404, detail="dish not found")

    def update(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
        dish: Dish,
    ):
        submenu = (
            self.session.query(SubmenuModel)
            .filter(
                SubmenuModel.id == submenu_id
                and SubmenuModel.menu_id == api_test_menu_id
            )
            .first()
        )
        if submenu is not None:
            for a in submenu.dishes:
                if a.id == dish_id:
                    if dish.title:
                        a.title = dish.title
                    if dish.description:
                        a.description = dish.description
                    if dish.price:
                        a.price = dish.price
                    self.session.commit()
                    self.session.refresh(a)
                    return {
                        "id": a.id,
                        "title": a.title,
                        "description": a.description,
                        "price": format_price(a.price),
                    }
            raise HTTPException(status_code=404, detail="Dish not found")
        raise HTTPException(status_code=404, detail="Submenu not found")

    def delete(
        self,
        api_test_menu_id: Union[uuid.UUID, None],
        submenu_id: Union[uuid.UUID, None],
        dish_id: Union[uuid.UUID, None],
    ):
        submenu = (
            self.session.query(SubmenuModel)
            .filter(
                SubmenuModel.id == submenu_id
                and SubmenuModel.menu_id == api_test_menu_id
            )
            .first()
        )
        for a in submenu.dishes:
            if a.id == dish_id:
                self.session.delete(a)
                self.session.commit()
                return {"message": "dish was deleted successful"}
        raise HTTPException(status_code=404, detail="dish not found")
