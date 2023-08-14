import uuid

# Third Party
from fastapi import Depends, APIRouter
from fastapi import BackgroundTasks

# Library
from app.models.models import Dish, Menu, Submenu
from app.services.DishService import DishService
from app.services.MenuService import MenuService
from app.services.SubmenuService import SubmenuService

app = APIRouter()

background_tasks = BackgroundTasks()


@app.post('/api/v1/menus/', status_code=201)
async def create_new_menu(create_menu: Menu, menu: MenuService = Depends()) -> dict:
    return await menu.create(create_menu, '/api/v1/menus/')


@app.get('/api/v1/menus/{menu_id}')
async def get_menu(menu_id: uuid.UUID, menu: MenuService = Depends()) -> dict:
    return await menu.get(menu_id, '/api/v1/menus/')


@app.get('/api/v1/menus/')
async def get_all_menus(menu: MenuService = Depends()):
    return await menu.get_all('/api/v1/menus/')


@app.patch('/api/v1/menus/{menu_id}')
async def update_concreate_menu(
        menu_id: uuid.UUID, updated_menu: Menu, menu: MenuService = Depends()
) -> Menu:
    return await menu.update(menu_id, updated_menu, '/api/v1/menus/', background_tasks)


@app.delete('/api/v1/menus/{menu_id}')
async def delete_concreate_menu(
        menu_id: uuid.UUID, menu: MenuService = Depends()
) -> dict:
    return await menu.delete(menu_id, '/api/v1/menus/', background_tasks)


@app.post('/api/v1/menus/{menu_id}/submenus/', status_code=201)
async def create_new_submenu(
        menu_id: uuid.UUID,
        submenu_new: Submenu,
        submenu: SubmenuService = Depends(),
):
    return await submenu.create(menu_id, submenu_new, '/api/v1/menus/')


@app.get('/api/v1/menus/{menu_id}/submenus/')
async def get_all_submenus(
        menu_id: uuid.UUID, submenu: SubmenuService = Depends()
) -> list:
    return await submenu.get_all(menu_id, '/api/v1/menus/')


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def get_concreate_submenu(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        submenu: SubmenuService = Depends(),
) -> dict:
    return await submenu.get(menu_id, submenu_id, '/api/v1/menus/')


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def update_existing_submenu(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        updated_submenu: Submenu,
        submenu: SubmenuService = Depends(),
) -> Submenu:
    return await submenu.update(
        menu_id, submenu_id, updated_submenu, '/api/v1/menus/', background_tasks
    )


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def delete_existing_submenu(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        submenu: SubmenuService = Depends(),
) -> dict:
    return await submenu.delete(menu_id, submenu_id, '/api/v1/menus/', background_tasks)


@app.post(
    '/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/',
    status_code=201,
)
async def create_new_dish(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_new: Dish,
        dish: DishService = Depends(),
) -> dict:
    return await dish.create(menu_id, submenu_id, dish_new, '/api/v1/menus/')


@app.get('/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes/')
async def show_all_dishes(
        api_test_menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish: DishService = Depends(),
) -> list:
    return await dish.get_all(api_test_menu_id, submenu_id, '/api/v1/menus/')


@app.get(
    '/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
)
async def show_concreate_dish(
        api_test_menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        dish: DishService = Depends(),
) -> dict:
    return await dish.get(api_test_menu_id, submenu_id, dish_id, '/api/v1/menus/')


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def update_existing_dish(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        updated_dish: Dish,
        dish: DishService = Depends(),
) -> Dish:
    return await dish.update(
        menu_id, submenu_id, dish_id, updated_dish, '/api/v1/menus/', background_tasks
    )


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_existing_dish(
        menu_id: uuid.UUID,
        submenu_id: uuid.UUID,
        dish_id: uuid.UUID,
        dish: DishService = Depends(),
) -> dict:
    return await dish.delete(menu_id, submenu_id, dish_id, '/api/v1/menus/', background_tasks)


@app.get('/menus/')
async def get_menus(
        menu: MenuService = Depends()):
    response = await menu.menus()
    return response
