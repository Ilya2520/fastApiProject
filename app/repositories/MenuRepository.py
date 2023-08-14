# Standard Library
import uuid

# Third Party
from fastapi import Depends, HTTPException
from sqlalchemy import select

from sqlalchemy.sql import text
from sqlalchemy.orm import selectinload

# Library

from app.database.database import AsyncSession as Session, SubmenuModel
from app.database.database import get_session as get_db
from app.database.database import (
    MenuModel,
    get_submenu_count,
    get_submenu_dishes,
)
from app.models.models import Menu
from app.repositories.Repository import Repository


class MenuRepository(Repository):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session)
        self.model = Menu

    async def create(
            self,
            menu: Menu,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
    ) -> dict:
        if menu.id:
            db_menu = MenuModel(id=menu.id, title=menu.title, description=menu.description)
        else:
            db_menu = MenuModel(title=menu.title, description=menu.description)
        self.session.add(db_menu)
        await self.session.commit()
        db_menu1 = {
            'id': db_menu.id,
            'title': db_menu.title,
            'description': db_menu.description,
            'submenus': [],
            'submenu_count': 0,
            'dishes_count': 0,
        }
        return db_menu1

    async def get(
            self,
            menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
    ):
        db_menu = await self.session.get(MenuModel, menu_id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail='menu not found')
        else:
            submenus_count = await get_submenu_count(self.session, db_menu.id)  # type: ignore
            submenus_with_dishes = await get_submenu_dishes(self.session, db_menu.id)  # type: ignore

            submenu_info = [
                {
                    'id': submenu.id,
                    'title': submenu.title,
                    'description': submenu.description,
                    'dishes_count': submenu.dishes_count,
                }
                for submenu in submenus_with_dishes
            ]
            menu_info = {
                'id': db_menu.id,
                'title': db_menu.title,
                'description': db_menu.description,
                'submenus_count': submenus_count,
                'submenus': submenu_info,
                'dishes_count': sum(
                    submenu.dishes_count for submenu in submenus_with_dishes
                ),
            }
            return menu_info

    async def get_all(
            self,
            api_test_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
    ):
        async with self.session:
            all_menus = await self.session.scalars(select(MenuModel))
            res = all_menus.all()
            menus_info = []
            for menu in res:
                submenus_count = await get_submenu_count(self.session, menu.id)
                submenus_with_dishes = await get_submenu_dishes(self.session, menu.id)  # type: ignore

                submenu_info = [
                    {
                        'id': submenu.id,
                        'title': submenu.title,
                        'description': submenu.description,
                        'dishes_count': submenu.dishes_count,
                    }
                    for submenu in submenus_with_dishes
                ]

                menus_info.append(
                    {
                        'id': menu.id,
                        'title': menu.title,
                        'description': menu.description,
                        'submenus': submenu_info,
                        'submenus_count': submenus_count,
                        'dishes_count': sum(
                            submenu.dishes_count
                            for submenu in submenus_with_dishes
                        ),
                    }
                )
        print(menus_info)
        return menus_info

    async def update(
            self,
            target_menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
            menu: Menu,
    ):
        if target_menu_id is None:
            raise HTTPException(
                status_code=400, detail='Invalid target_menu_id'
            )
        db_menu = await self.session.get(MenuModel, target_menu_id)

        if db_menu is not None:
            if menu and menu.title:
                db_menu.title = menu.title
            if menu and menu.description:
                db_menu.description = menu.description
            await self.session.commit()
            await self.session.refresh(db_menu)
            return {
                'id': db_menu.id,
                'title': db_menu.title,
                'description': db_menu.description,
            }
        else:
            raise HTTPException(status_code=404, detail='Menu not found')

    async def delete(
            self,
            menu_id: uuid.UUID | None,
            submenu_id: uuid.UUID | None,
            dish_id: uuid.UUID | None,
    ):
        db_menu = await self.session.get(MenuModel, menu_id)
        if db_menu:
            for submenu in db_menu.submenus:
                await self.session.delete(submenu)
            await self.session.delete(db_menu)
            await self.session.commit()
            return {'message': 'successful'}
        return {'message': 'error'}

    async def get_all_menus1(self):
        menus = (
            await self.session.scalars(
                select(MenuModel).options(selectinload(MenuModel.submenus).options(selectinload(SubmenuModel.dishes))))
        )
        return menus.first()

    async def get_all_menus(self):
        query = text("""
            SELECT
                m.id AS menu_id,
                m.title AS menu_title,
                s.id AS submenu_id,
                s.title AS submenu_title,
                d.id AS dish_id,
                d.title AS dish_title
            FROM menus m
            JOIN submenus s ON m.id = s.menu_id
            LEFT JOIN dishes d ON s.id = d.submenu_id
        """)

        result = await self.session.execute(query)
        result = result.all()
        menus = {}

        for row in result:
            menu_id, menu_title, submenu_id, submenu_title, dish_id, dish_title = row

            if menu_id not in menus:
                menus[menu_id] = {
                    'menu_id': menu_id,
                    'menu_title': menu_title,
                    'submenus': {}
                }

            if submenu_id not in menus[menu_id]['submenus']:
                menus[menu_id]['submenus'][submenu_id] = {
                    'submenu_id': submenu_id,
                    'submenu_title': submenu_title,
                    'dishes': []
                }

            if dish_id:
                menus[menu_id]['submenus'][submenu_id]['dishes'].append({
                    'dish_id': dish_id,
                    'dish_title': dish_title
                })

        return list(menus.values())
