# Standard Library

import uuid

# Third Party
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Library
from app.database.database import (
    MenuModel,
    SubmenuModel,
    format_price,
    get_submenu_dishes_count
)

from app.database.database import AsyncSession as Session
from app.database.database import get_session as get_db
from app.models.models import Submenu
from app.repositories.Repository import Repository


class SubmenuRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Submenu

    async def get_all(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None = None,
    ):

        menu = await self.session.scalars(
            select(MenuModel).where(MenuModel.id == api_test_menu_id).options(
                selectinload(MenuModel.submenus, SubmenuModel.dishes)))
        menu = menu.first()
        if menu is None:
            return []
        submenu_info = []
        for submenu in menu.submenus:
            dishes_count = await get_submenu_dishes_count(self.session, submenu.id)
            submenu_dishes = []
            for dish in submenu.dishes:
                submenu_dishes.append(
                    {
                        'id': dish.id,
                        'title': dish.title,
                        'description': dish.description,
                        'price': dish.price,
                    }
                )
            submenu_info.append(
                {
                    'id': submenu.id,
                    'title': submenu.title,
                    'description': submenu.description,
                    'dishes': submenu_dishes,
                    'dishes_count': dishes_count,
                }
            )
        return submenu_info

    async def create(
            self,
            submenu: Submenu | SubmenuModel,
            menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
    ):
        if type(submenu) is SubmenuModel:
            nw_submenu = submenu
        else:
            nw_submenu = SubmenuModel(
                title=submenu.title, description=submenu.description
            )
        db_menu = (await self.session.scalars(
            select(MenuModel).where(MenuModel.id == menu_id).options(selectinload(MenuModel.submenus))))
        db_menu = db_menu.first()
        if db_menu is None:
            return []
        db_menu.submenus.append(nw_submenu)
        self.session.add(nw_submenu)
        await self.session.commit()

        return {
            'id': nw_submenu.id,
            'title': nw_submenu.title,
            'description': nw_submenu.description,
            'dishes_count': 0,
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
        if submenu:
            dishes_count = await get_submenu_dishes_count(
                self.session, submenu_id  # type: ignore
            )
            submenu_info = {
                'id': submenu.id,
                'title': submenu.title,
                'description': submenu.description,
                'dishes_count': dishes_count,
            }
            dishes_info = [
                {
                    'id': dish.id,
                    'title': dish.title,
                    'description': dish.description,
                    'price': format_price(dish.price),
                }
                for dish in submenu.dishes
            ]
            submenu_info['dishes'] = dishes_info
            return submenu_info
        raise HTTPException(status_code=404, detail='submenu not found')

    async def update(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
            update_submenu: Submenu,
    ):
        submenu = (
            await self.session.get(SubmenuModel, submenu_id)
        )
        if submenu:
            if update_submenu.title:
                submenu.title = update_submenu.title
            if update_submenu.description:
                submenu.description = update_submenu.description
            await self.session.commit()
            await self.session.refresh(submenu)
            return {
                'id': submenu.id,
                'title': submenu.title,
                'description': submenu.description,
            }
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
        if submenu:
            for dish in submenu.dishes:
                await self.session.delete(dish)
            await self.session.delete(submenu)
            await self.session.commit()
            return {'message': 'successful delete'}
        raise HTTPException(status_code=404, detail='submenu not found')
