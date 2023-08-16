import uuid

import openpyxl

from app.database.database import MenuModel, DishModel, SubmenuModel, async_session
from app.repositories.DishRepository import DishRepository
from app.repositories.MenuRepository import MenuRepository
from app.repositories.SubmenuRepository import SubmenuRepository
from app.services.RedisService import RedisService

import jsondiff
import pandas as pd

PATH = '/app/admin/Menu.xlsx'


async def initialize_exc():
    async with async_session() as session:
        menu_repository = MenuRepository(session)
        submenu_repository = SubmenuRepository(session)
        dish_repository = DishRepository(session)
        redis_service = RedisService()

        excel_service = ExcelService(menu_repository, submenu_repository, dish_repository, redis_service)
        return excel_service


async def change(st, id: uuid.UUID):
    # root_dir = os.path.abspath(__file__)
    # xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
    xlsx_file_path = PATH
    workbook = openpyxl.load_workbook(xlsx_file_path)
    sheet = workbook.active
    sheet[st] = str(id)
    workbook.save(xlsx_file_path)


def to_uuid(id):
    try:
        uuid.UUID(str(id))
        return True
    except ValueError:
        print('value error')
        return False


def get_list(lst: list, st, end):
    result = []
    for i in range(len(lst)):
        if st <= lst[i] <= end:
            result.append(lst[i])
    return result


def get_excel_sheet(row, column):
    mas = ['A', 'B', 'C']
    column = mas[column]
    return column + str(row + 1)


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


async def cnt(df: pd.DataFrame):
    menus_count = len(df[0].dropna().index)
    submenus_count = len(df[1].dropna().index)
    dish_count = len(df[2].dropna().index)
    return {'menus': menus_count, 'submenus': submenus_count, 'dishes': dish_count}


class ExcelService:
    def __init__(self, menu_repository: MenuRepository, submenu_repository: SubmenuRepository,
                 dish_repository: DishRepository, redis_service: RedisService):
        self.menu_repository = menu_repository
        self.submenu_repository = submenu_repository
        self.dish_repository = dish_repository
        self.service = redis_service

    async def check_delete_or_update(self, prev: list, curr: list, menu_id: uuid.UUID | None = None,
                                     submenu_id: uuid.UUID | None = None):
        previous = []
        current = []
        for i in prev:
            previous.append(i['id'])
        print('prev', previous)
        for i in curr:
            current.append(i['id'])
        deleted = []
        for ind in previous:
            print(ind)
            if ind not in current and to_uuid(ind):
                print('app dele')
                deleted.append(ind)
        created = []
        for ind in current:
            if ind not in previous and to_uuid(ind):
                created.append(ind)
        if len(deleted) > 0:
            print('deleted', deleted)
            for i in deleted:
                for j in prev:
                    if j['id'] == i:
                        if submenu_id:
                            await self.dish_repository.delete(menu_id, submenu_id, i)
                        elif menu_id:
                            await self.submenu_repository.delete(menu_id, i, None)
                        else:
                            await self.menu_repository.delete(i, None, None)

                        break
        if len(created) > 0:
            for i in created:
                print('created', created)
                for j in curr:
                    if j['id'] == i:
                        if submenu_id:
                            await self.dish_repository.create(
                                DishModel(id=i, title=j['title'], description=j['desc'], price=j['subs']),
                                menu_id, submenu_id,
                            )
                        elif menu_id:
                            await self.submenu_repository.create(
                                SubmenuModel(id=i, title=j['title'], description=j['desc']),
                                menu_id, submenu_id
                            )
                            if 'subs' in j:
                                await self.check_delete_or_update([], j['subs'], menu_id, j['id'])
                        else:
                            await self.menu_repository.create(
                                MenuModel(id=i, title=j['title'], description=j['desc']),
                                menu_id, submenu_id,
                            )
                            if 'subs' in j:
                                await self.check_delete_or_update([], j['subs'], j['id'])
                        break
        # for i in prev:
        #     if i not in curr:
        #         print("delete:", i)
        # for i in curr:
        #     if i not in prev:
        #         print("update", i)

    async def check(self, prev_data, current_data, menu_id: uuid.UUID | None = None,
                    submenu_id: uuid.UUID | None = None):
        print('check func')
        await self.check_delete_or_update(prev_data, current_data, menu_id, submenu_id)
        for prev_item in prev_data:
            for curr_item in current_data:
                if prev_item['id'] == curr_item['id'] and prev_item != curr_item:
                    df = jsondiff.diff(prev_item, curr_item)
                    cur_id = curr_item.get('id')
                    upd = {}
                    for i in df.keys():

                        if i != 'subs':
                            upd[i] = curr_item.get(i)
                        else:
                            if df.get('subs') is not list:
                                upd['price'] = curr_item.get('subs')
                    if submenu_id:
                        upd['menu_id'] = menu_id
                        upd['sub_id'] = submenu_id
                        upd['dish_id'] = cur_id
                        if len(upd) != 3:
                            await self.update_dish(upd)
                    elif menu_id:
                        upd['menu_id'] = menu_id
                        upd['sub_id'] = cur_id
                        if len(upd) != 3:
                            await self.update_submenu(upd)
                    else:
                        upd['menu_id'] = cur_id
                        if len(upd) != 1:
                            await self.update_menu(upd)
                    if 'subs' in df.keys():
                        if menu_id and submenu_id is None:
                            await self.check(prev_item['subs'], curr_item['subs'], menu_id, cur_id)
                        elif menu_id is None:
                            await self.check(prev_item['subs'], curr_item['subs'], cur_id)

    async def update_dish(self, dish: dict):
        a = DishModel()
        if 'desc' in dish.keys():
            a.description = dish['desc']
        if 'title' in dish.keys():
            a.title = dish['title']
        if 'price' in dish.keys():
            a.price = dish['price']
        print('update dish', a.description, a.title, a.price)
        c = await self.dish_repository.update(dish['menu_id'], dish['sub_id'], dish['dish_id'], a)
        return c

    async def update_submenu(self, submenu: dict):

        a = SubmenuModel()
        if 'desc' in submenu.keys():
            a.description = submenu['desc']
        if 'title' in submenu.keys():
            a.title = submenu['title']
        print('updated submenu', a.description, a.title)
        c = await self.submenu_repository.update(submenu['menu_id'], submenu['sub_id'], None, a)
        return c

    async def update_menu(self, menu: dict):
        a = MenuModel()
        if 'desc' in menu.keys():
            a.description = menu['desc']
        if 'title' in menu.keys():
            a.title = menu['title']
        c = await self.menu_repository.update(menu['menu_id'], None, None, a)
        return c

    def get_params(self, df: pd.DataFrame, ind, start, end):
        lst = get_list(list(df[ind].dropna().index), start, end)
        dfs = []
        for i in range(len(lst)):
            tit1 = df[ind][lst[i]]
            tit2 = df[ind + 1][lst[i]]
            tit3 = df[ind + 2][lst[i]]
            if lst[i] != lst[-1]:
                if ind != 2:
                    sub = self.get_params(df, ind + 1, lst[i] + 1, lst[i + 1] - 1)
                else:
                    sub = df[ind + 3][lst[i]]
                sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
                       'subs': sub}

            else:
                if ind != 2:
                    sub = self.get_params(df, ind + 1, lst[i] + 1, end)
                else:
                    sub = df[ind + 3][lst[i]]
                sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
                       'subs': sub}

            dfs.append(sel)
        return dfs

    def get_from_xlsx(self):
        # root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        # root_dir = os.path.abspath(os.path.join(root_dir, '..'))
        # xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
        xlsx_file_path = PATH
        df = pd.read_excel(xlsx_file_path, header=None)
        dfs = self.get_params(df, 0, 0, df.shape[0])
        return dfs, df

    async def add_from_excel(self):
        data, data2 = self.get_from_xlsx()
        for menu in data:
            menu_id_excel = menu.get('id')
            if to_uuid(menu_id_excel):
                create_menu = MenuModel(id=menu_id_excel, title=menu.get('title'), description=menu.get('desc'))
            else:
                create_menu = MenuModel(title=menu.get('title'), description=menu.get('desc'))
            res_menu = await self.menu_repository.create(create_menu, None, None)
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
                res_sub = await self.submenu_repository.create(create_submenu, menu_id, None)
                submenu_id = res_sub['id']
                if submenu_id_excel != submenu_id:
                    await change(subs.get('sheet'), submenu_id)
                for dish in subs.get('subs'):
                    dish_id_excel = dish.get('id')
                    if to_uuid(dish_id_excel):
                        create_dish = DishModel(id=dish_id_excel, title=dish.get('title'),
                                                description=dish.get('desc'),
                                                price=dish.get('subs'))
                    else:
                        create_dish = DishModel(title=dish.get('title'), description=dish.get('desc'),
                                                price=dish.get('subs'))
                    res_dish = await self.dish_repository.create(create_dish, menu_id, submenu_id)
                    if dish_id_excel != res_dish['id']:
                        await change(dish.get('sheet'), res_dish['id'])

    # async def check_changes(self, previous_data, current_data):
    #     for prev_item in previous_data:
    #         for curr_item in current_data:
    #             if prev_item['id'] == curr_item['id'] and prev_item != curr_item:
    #                 df = jsondiff.diff(prev_item, curr_item)
    #                 menu_id = curr_item.get('id')
    #                 upd = {}
    #                 for i in df.keys():
    #                     if i != 'subs':
    #                         upd[i] = curr_item.get(i)
    #                     else:
    #                         prev_sub, cur_sub = prev_item.get('subs'), curr_item.get('subs')
    #                         lens = max(len(prev_sub), len(cur_sub))
    #                         if len(prev_sub) != len(cur_sub):
    #                             self.check_delete_or_update(prev_sub, cur_sub)
    #                         else:
    #                             for h in range(lens):
    #                                 df_between_subs = jsondiff.diff(prev_sub[h], cur_sub[h])
    #                                 sub_id = cur_sub[h].get('id')
    #                                 sub_upd = {"sub_id": sub_id}
    #                                 for jk in df_between_subs.keys():
    #                                     if jk != 'subs':
    #                                         sub_upd[jk] = cur_sub[h].get(jk)
    #                                     else:
    #                                         prev_dish, cur_dish = prev_sub[h]['subs'], cur_sub[h]['subs']
    #                                         for le in range(len(prev_dish)):
    #                                             df_between_dish = jsondiff.diff(prev_dish[le], cur_dish[le])
    #                                             dish_id = cur_dish[le].get('id')
    #                                             dish_upd = {"dish_id": dish_id}
    #                                             for d in df_between_dish.keys():
    #                                                 if d != 'subs':
    #                                                     dish_upd[d] = cur_dish[le].get(d)
    #                                                 else:
    #                                                     dish_upd['price'] = cur_dish[le].get(d)
    #                                             dish_upd['menu_id'] = menu_id
    #                                             dish_upd['sub_id'] = sub_id
    #                                             if len(dish_upd.keys()) != 3:
    #                                                 al = await self.update_dish(dish_upd)
    #                                 sub_upd["menu_id"] = menu_id
    #                                 if len(sub_upd.keys()) != 2:
    #                                     al = await self.update_submenu(sub_upd)
    #                                     print(sub_upd, al)
    #                 upd['menu_id'] = menu_id
    #                 if len(upd.keys()) != 1:
    #                     al = await self.update_menu(upd)
    #                     print(upd, al)
    async def del_id(self, cur, menu_id: uuid.UUID | None = None,
                     submenu_id: uuid.UUID | None = None):
        print(cur)
        if submenu_id:
            print('d')
            for i in cur['subs']:
                i['id'] = 0
            print(cur)
            return cur
        elif menu_id:
            print('ss')
            for i in cur['subs']:
                i = await self.del_id(i, menu_id, i['id'])
                i['id'] = 0
            print('ss cur')
            return cur
        else:
            print('m')
            for i in cur['subs']:
                cur['subs'] = await self.del_id(i, i['id'])
                i['id'] = 0
            print('ss cur')
            return cur
