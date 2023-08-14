# Standard Library

import uuid

# Third Party
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Library
from app.database.database import DishModel, SubmenuModel, format_price
from app.database.database import AsyncSession as Session
from app.database.database import get_session as get_db
from app.models.models import Dish
from app.repositories.Repository import Repository


class DishRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Dish

    async def get_all(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
    ):

        submenu = await self.session.scalars(
            select(SubmenuModel).where(SubmenuModel.id == submenu_id).options(selectinload(SubmenuModel.dishes)))
        submenu = submenu.first()
        if submenu is None:
            return []
        dishes_info = []
        for dish in submenu.dishes:
            dishes_info.append(
                {
                    'id': dish.id,
                    'title': dish.title,
                    'description': dish.description,
                    'price': format_price(dish.price),
                }
            )
        return dishes_info

    async def create(
            self,
            dish: Dish,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
    ) -> dict:
        if dish.id:
            nw_dish = DishModel(
                id=dish.id,
                title=dish.title, description=dish.description, price=dish.price
            )
        else:
            nw_dish = DishModel(
                title=dish.title, description=dish.description, price=dish.price
            )
        submenu = await self.session.scalars(
            select(SubmenuModel).where(SubmenuModel.id == submenu_id).options(selectinload(SubmenuModel.dishes)))
        submenu = submenu.first()
        if submenu is None:
            raise HTTPException(status_code=404, detail='Submenu not found')
        submenu.dishes.append(nw_dish)
        self.session.add(nw_dish)
        await self.session.commit()
        return {
            'id': nw_dish.id,
            'title': nw_dish.title,
            'description': nw_dish.description,
            'price': format_price(nw_dish.price),
        }

    async def get(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
    ):

        submenu = await self.session.scalars(
            select(SubmenuModel).where(SubmenuModel.id == submenu_id).options(selectinload(SubmenuModel.dishes)))
        submenu = submenu.first()
        for a in submenu.dishes:
            if a.id == dish_id:
                return {
                    'id': a.id,
                    'title': a.title,
                    'description': a.description,
                    'price': format_price(a.price),
                }
        raise HTTPException(status_code=404, detail='dish not found')

    async def update(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
            dish: Dish,
    ):
        submenu = await self.session.scalars(
            select(SubmenuModel).where(SubmenuModel.id == submenu_id).options(selectinload(SubmenuModel.dishes)))
        submenu = submenu.first()
        if submenu is not None:
            for a in submenu.dishes:
                if a.id == dish_id:
                    if dish.title:
                        a.title = dish.title
                    if dish.description:
                        a.description = dish.description
                    if dish.price:
                        a.price = dish.price
                    await self.session.commit()
                    await self.session.refresh(a)
                    return {
                        'id': a.id,
                        'title': a.title,
                        'description': a.description,
                        'price': format_price(a.price),
                    }
            raise HTTPException(status_code=404, detail='Dish not found')
        raise HTTPException(status_code=404, detail='Submenu not found')

    async def delete(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
    ):
        submenu = await self.session.scalars(
            select(SubmenuModel).where(SubmenuModel.id == submenu_id).options(selectinload(SubmenuModel.dishes)))
        submenu = submenu.first()
        for a in submenu.dishes:
            if a.id == dish_id:
                await self.session.delete(a)
                await self.session.commit()
                return {'message': 'dish was deleted successful'}
        raise HTTPException(status_code=404, detail='dish not found')
