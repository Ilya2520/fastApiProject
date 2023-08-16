# Standard Library
# Third Party
from fastapi import FastAPI
from sqlalchemy import select

# Library
from app.database.database import init_models, MenuModel, async_session, SubmenuModel, DishModel
from app.services.ExcelService import initialize_exc
from app.services.RedisService import RedisService
from app.crud.crud import app as crud

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
    await clear_redis_on_startup()
    start = await initialize_exc()
    await start.add_from_excel()

#
# def get_list(lst: list, st, end):
#     result = []
#     for i in range(len(lst)):
#         if st <= lst[i] <= end:
#             result.append(lst[i])
#     return result

#
# def get_params(df: pd.DataFrame, ind, start, end):
#     lst = get_list(list(df[ind].dropna().index), start, end)
#     dfs = []
#     for i in range(len(lst)):
#         tit1 = df[ind][lst[i]]
#         tit2 = df[ind + 1][lst[i]]
#         tit3 = df[ind + 2][lst[i]]
#         if lst[i] != lst[-1]:
#             if ind != 2:
#                 sub = get_params(df, ind + 1, lst[i] + 1, lst[i + 1] - 1)
#             else:
#                 sub = df[ind + 3][lst[i]]
#             sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
#                    'subs': sub}
#
#         else:
#             if ind != 2:
#                 sub = get_params(df, ind + 1, lst[i] + 1, end)
#             else:
#                 sub = df[ind + 3][lst[i]]
#             sel = {'id': tit1, 'sheet': get_excel_sheet(lst[i], ind), 'title': tit2, 'desc': tit3,
#                    'subs': sub}
#
#         dfs.append(sel)
#     return dfs

#
# def separate_df(df: pd.DataFrame, ind):
#     lst = list(df[ind].dropna().index)
#     end = len(df[ind])
#     dfs = []
#     for i in range(len(lst)):
#         if lst[i] != lst[-1]:
#             subset_df = df.iloc[lst[i]:lst[i + 1], ind + 1:6]
#         else:
#             subset_df = df.iloc[lst[i]:end + 1, ind + 1:6]
#         dfs.append(subset_df)
#     return dfs

#
# def to_structure(df: pd.DataFrame):
#     # menu = {"title": df[1][i], "description": df[1][i], "submenus": []}
#     print('a')

#
# def get_from_xlsx():
#     root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
#     xlsx_file_path = os.path.join(root_dir, 'Menu.xlsx')
#     print(xlsx_file_path)
#     df = pd.read_excel(xlsx_file_path, header=None)
#     dfs = get_params(df, 0, 0, df.shape[0])
#     print('||||||||||||||||||||||||')
#     return dfs

#
#
# @app.get('/a')
# async def go_check():
#     await run_async_check_excel_changes()
#     return {'detail': 'good celery response'}
