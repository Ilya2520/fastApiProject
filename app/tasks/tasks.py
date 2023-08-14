import logging
import os
import jsondiff
import pandas as pd
from celery import Celery
from app.services.RedisService import RedisService

celery = Celery('tasks', broker='redis://redis:6379/0')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task()
async def check_excel_changes():
    previous_data, cn = await RedisService().get_excel_data()
    current_data, df = get_from_xlsx()
    count_ = await cnt(df)
    if previous_data:
        if cn == count_:
            print('No delete or create')
        await check_changes(previous_data, current_data)
    # if a == []:
    #     print("no Changes")
    # else:
    #     print("was changes")
    #     print(a)
    #     await updates_data(a)
    await RedisService().save_excel_data(current_data, count_)


celery.conf.beat_schedule = {
    'run-me-every-15-seconds': {
        'task': 'tasks.check_excel_changes',
        'schedule': 15.0
    }
}


async def cnt(df: pd.DataFrame):
    menus_count = len(df[0].dropna().index)
    submenus_count = len(df[1].dropna().index)
    dish_count = len(df[2].dropna().index)
    return {'menus': menus_count, 'submenus': submenus_count, 'dishes': dish_count}


async def updates_data(a: list):
    for i in a:
        print(to_json(i))


async def check_for_create(previous_data, current_data):
    pass


def some(arr):
    res = {}
    if arr[1] is dict:
        if 'id' in arr[1].keys():
            print('JJJ')
        else:
            print(get_json(arr[1]))
    else:
        res['id'] = arr[0]
    print(res)


def get_json(arr):
    r = {'id': arr[0]}
    for a in arr[1:len(arr)]:
        for i in a.keys():
            r[i] = a[i]
    return r


def to_json(arr):
    for i in arr:
        print(i)


async def check_changes(previous_data, current_data):
    for prev_item in previous_data:
        for curr_item in current_data:
            if prev_item['id'] == curr_item['id'] and prev_item != curr_item:
                df = jsondiff.diff(prev_item, curr_item)
                result = {}
                menu_id = curr_item.get('id')
                result[menu_id] = [menu_id]
                upd = {}
                for i in df.keys():
                    if i != 'subs':
                        upd[i] = curr_item.get(i)
                    else:
                        prev_sub, cur_sub = prev_item.get('subs'), curr_item.get('subs')
                        for h in range(len(prev_sub)):
                            df_between_subs = jsondiff.diff(prev_sub[h], cur_sub[h])

                            sub_id = cur_sub[h].get('id')
                            result[sub_id] = [sub_id]
                            for jk in df_between_subs.keys():
                                if jk != 'subs':
                                    result[sub_id].append({f'{jk}': cur_sub[h].get(jk)})
                                    # sub = {f'{jk}': curr_item.get('subs')[h].get(jk)}
                                    # submenu['details'] = sub
                                else:
                                    prev_dish, cur_dish = prev_sub[h]['subs'], cur_sub[h]['subs']
                                    for le in range(len(prev_dish)):
                                        df_between_dish = jsondiff.diff(prev_dish[le], cur_dish[le])
                                        dish_id = cur_dish[le].get('id')
                                        result[dish_id] = [dish_id]
                                        for d in df_between_dish.keys():
                                            if d != 'subs':
                                                result[dish_id].append({f'{d}': cur_dish[le].get(d)})
                                            else:
                                                result[dish_id].append({'price': cur_dish[le].get(d)})
                                        if len(result[dish_id]) != 1:
                                            result[sub_id].append({'dishes': get_json(result[dish_id])})
                            if len(result[sub_id]) != 1:
                                result[menu_id].append({'submenus': get_json(result[sub_id])})
                    upd['id'] = menu_id
                print(upd)


async def changes(previous_data, current_data):
    all = []
    for prev_item in previous_data:
        for curr_item in current_data:
            if prev_item['id'] == curr_item['id'] and prev_item != curr_item:
                df = jsondiff.diff(prev_item, curr_item)
                result = {}
                menu_id = curr_item.get('id')
                result[menu_id] = [menu_id]
                for i in df.keys():
                    if i != 'subs':
                        result[menu_id].append(
                            {f'{i}': curr_item.get(f'{i}')})
                    else:
                        prev_sub, cur_sub = prev_item.get('subs'), curr_item.get('subs')
                        for h in range(len(prev_sub)):
                            df_between_subs = jsondiff.diff(prev_sub[h], cur_sub[h])

                            sub_id = cur_sub[h].get('id')
                            result[sub_id] = [sub_id]
                            for jk in df_between_subs.keys():
                                if jk != 'subs':
                                    result[sub_id].append({f'{jk}': cur_sub[h].get(jk)})
                                    # sub = {f'{jk}': curr_item.get('subs')[h].get(jk)}
                                    # submenu['details'] = sub
                                else:
                                    prev_dish, cur_dish = prev_sub[h]['subs'], cur_sub[h]['subs']
                                    for le in range(len(prev_dish)):
                                        df_between_dish = jsondiff.diff(prev_dish[le], cur_dish[le])
                                        dish_id = cur_dish[le].get('id')
                                        result[dish_id] = [dish_id]
                                        for d in df_between_dish.keys():
                                            if d != 'subs':
                                                result[dish_id].append({f'{d}': cur_dish[le].get(d)})
                                            else:
                                                result[dish_id].append({'price': cur_dish[le].get(d)})
                                        if len(result[dish_id]) != 1:
                                            result[sub_id].append({'dishes': get_json(result[dish_id])})
                            if len(result[sub_id]) != 1:
                                result[menu_id].append({'submenus': get_json(result[sub_id])})
                all.append(result[menu_id])
    return all


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


def get_from_xlsx():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    root_dir = os.path.abspath(os.path.join(root_dir, '..'))
    xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
    print(xlsx_file_path)
    df = pd.read_excel(xlsx_file_path, header=None)
    dfs = get_params(df, 0, 0, df.shape[0])
    print('||||||||||||||||||||||||')
    return dfs, df


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
