# Standard Library
# Third Party
import os
import uuid
from itertools import count

import openpyxl
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import select

# Library
from app.database.database import init_models, MenuModel, async_session, SubmenuModel, DishModel
from app.repositories.DishRepository import DishRepository
from app.repositories.MenuRepository import MenuRepository
from app.repositories.SubmenuRepository import SubmenuRepository
from app.services.RedisService import RedisService
from app.crud.crud import app as crud
from app.tasks.tasks import check_excel_changes

app = FastAPI()

app.include_router(crud)


async def clear_redis_on_startup() -> None:
    r = RedisService()
    await r.redis.flushall()


async def clear_db():
    async with async_session() as session:
        query = select(MenuModel)
        records1 = await session.execute(query)
        records2 = await session.execute(select(SubmenuModel))
        records3 = await session.execute(select(DishModel))
        for record in records1.scalars():
            await session.delete(record)
        for record in records2.scalars():
            await session.delete(record)
        for record in records3.scalars():
            await session.delete(record)
        await session.commit()


@app.on_event('startup')
async def startup_event():
    await init_models()
    await add_from_excel()


def get_excel_sheet(row, column):
    mas = ['A', 'B', 'C']
    column = mas[column]
    return column + str(row + 1)


def get_list(lst: list, st, end):
    result = []
    for i in range(len(lst)):
        if st <= lst[i] <= end:
            result.append(lst[i])
    return result


def get_params(df: pd.DataFrame, ind, start, end):
    lst = get_list(list(df[ind].dropna().index), start, end)
    dfs = []
    for i in range(len(lst)):
        tit1 = df[ind][lst[i]]
        tit2 = df[ind + 1][lst[i]]
        tit3 = df[ind + 2][lst[i]]
        if lst[i] != lst[-1]:
            if ind != 2:
                sub = get_params(df, ind + 1, lst[i] + 1, lst[i + 1] - 1)
            else:
                sub = df[ind + 3][lst[i]]
            sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
                   'subs': sub}

        else:
            if ind != 2:
                sub = get_params(df, ind + 1, lst[i] + 1, end)
            else:
                sub = df[ind + 3][lst[i]]
            sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
                   'subs': sub}

        dfs.append(sel)
    return dfs


def separate_df(df: pd.DataFrame, ind):
    lst = list(df[ind].dropna().index)
    end = len(df[ind])
    dfs = []
    for i in range(len(lst)):
        if lst[i] != lst[-1]:
            subset_df = df.iloc[lst[i]:lst[i + 1], ind + 1:6]
        else:
            subset_df = df.iloc[lst[i]:end + 1, ind + 1:6]
        dfs.append(subset_df)
    return dfs


def to_structure(df: pd.DataFrame):
    # menu = {"title": df[1][i], "description": df[1][i], "submenus": []}
    print('a')


def get_from_xlsx():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
    print(xlsx_file_path)
    df = pd.read_excel(xlsx_file_path, header=None)
    dfs = get_params(df, 0, 0, df.shape[0])
    print('||||||||||||||||||||||||')
    return dfs


async def change(st, id: uuid.UUID):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
    workbook = openpyxl.load_workbook(xlsx_file_path)
    sheet = workbook.active
    sheet[st] = str(id)
    workbook.save(xlsx_file_path)


def to_uuid(id):
    try:
        uuid.UUID(str(id))
        return True
    except ValueError:
        return False


async def add_from_excel():
    async with async_session() as session:
        data = get_from_xlsx()
        for menu in data:
            menu_id_excel = menu.get('id')
            if to_uuid(menu_id_excel):
                create_menu = MenuModel(id=menu_id_excel, title=menu.get('title'), description=menu.get('desc'))
            else:
                create_menu = MenuModel(title=menu.get('title'), description=menu.get('desc'))
            res_menu = await MenuRepository(session).create(create_menu, None, None)
            menu_id = res_menu['id']
            if menu_id_excel != menu_id:
                await change(menu['sheet'], menu_id)
            for subs in menu.get('subs'):
                submenu_id_excel = subs.get('id')
                if to_uuid(submenu_id_excel):
                    create_submenu = SubmenuModel(id=submenu_id_excel, title=subs.get('title'),
                                                  description=subs.get('desc'))
                else:
                    create_submenu = SubmenuModel(title=subs.get('title'),
                                                  description=subs.get('desc'))
                res_sub = await SubmenuRepository(session).create(create_submenu, menu_id, None)
                submenu_id = res_sub['id']
                if submenu_id_excel != submenu_id:
                    await change(subs.get('sheet'), submenu_id)
                for dish in subs.get('subs'):
                    dish_id_excel = dish.get('id')
                    if to_uuid(dish_id_excel):
                        create_dish = DishModel(id=dish_id_excel, title=dish.get('title'), description=dish.get('desc'),
                                                price=dish.get('subs'))
                    else:
                        create_dish = DishModel(title=dish.get('title'), description=dish.get('desc'),
                                                price=dish.get('subs'))
                    res_dish = await DishRepository(session).create(create_dish, menu_id, submenu_id)
                    if dish_id_excel != res_dish['id']:
                        await change(dish.get('sheet'), res_dish['id'])


async def cnt(df: pd.DataFrame):
    menus_count = count(df[0].dropna().index)
    submenus_count = count(df[1].dropna().index)
    dish_count = count(df[2].dropna().index)
    return {'menus': menus_count, 'submenus': submenus_count, 'dishes': dish_count}


@app.get('/a')
async def go_check():
    await check_excel_changes()
    return {'detail': 'good celery response'}
