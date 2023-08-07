# Standard Library
import uuid

# Third Party
from fastapi import Depends, FastAPI

# Library
from app.database.database import Session as db_session
from app.database.database import clear_database
from app.models.models import Dish, Menu, Submenu
from app.services.DishService import DishService
from app.services.MenuService import MenuService
from app.services.RedisService import RedisService
from app.services.SubmenuService import SubmenuService

app = FastAPI()


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def clear_db_on_startup() -> None:
    with db_session() as db:
        clear_database(db)


clear_db_on_startup()


def clear_redis_on_startup() -> None:
    r = RedisService()
    r.redis.flushall()


clear_redis_on_startup()


@app.post("/api/v1/menus/", status_code=201)
def create_new_menu(create_menu: Menu, menu: MenuService = Depends()) -> dict:
    return menu.create(create_menu, "/api/v1/menus/")


@app.get("/api/v1/menus/{menu_id}")
def get_menu(menu_id: uuid.UUID, menu: MenuService = Depends()) -> dict:
    return menu.get(menu_id, "/api/v1/menus/")


@app.get("/api/v1/menus/")
def get_all_menus(menu: MenuService = Depends()) -> list:
    return menu.get_all("/api/v1/menus/")


@app.patch("/api/v1/menus/{menu_id}")
def update_concreate_menu(
    menu_id: uuid.UUID, updated_menu: Menu, menu: MenuService = Depends()
) -> Menu:
    return menu.update(menu_id, updated_menu, "/api/v1/menus/")


@app.delete("/api/v1/menus/{menu_id}")
def delete_concreate_menu(
    menu_id: uuid.UUID, menu: MenuService = Depends()
) -> dict:
    return menu.delete(menu_id, "/api/v1/menus/")


@app.post("/api/v1/menus/{menu_id}/submenus/", status_code=201)
def create_new_submenu(
    menu_id: uuid.UUID,
    submenu_new: Submenu,
    submenu: SubmenuService = Depends(),
) -> dict:
    return submenu.create(menu_id, submenu_new, "/api/v1/menus/")


@app.get("/api/v1/menus/{menu_id}/submenus/")
def get_all_submenus(
    menu_id: uuid.UUID, submenu: SubmenuService = Depends()
) -> list:
    return submenu.get_all(menu_id, "/api/v1/menus/")


@app.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def get_concreate_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    submenu: SubmenuService = Depends(),
) -> dict:
    return submenu.get(menu_id, submenu_id, "/api/v1/menus/")


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def update_existing_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    updated_submenu: Submenu,
    submenu: SubmenuService = Depends(),
) -> Submenu:
    return submenu.update(
        menu_id, submenu_id, updated_submenu, "/api/v1/menus/"
    )


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}")
def delete_existing_submenu(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    submenu: SubmenuService = Depends(),
) -> dict:
    return submenu.delete(menu_id, submenu_id, "/api/v1/menus/")


@app.post(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/",
    status_code=201,
)
def create_new_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_new: Dish,
    dish: DishService = Depends(),
) -> dict:
    return dish.create(menu_id, submenu_id, dish_new, "/api/v1/menus/")


@app.get("/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes/")
def show_all_dishes(
    api_test_menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish: DishService = Depends(),
) -> list:
    return dish.get_all(api_test_menu_id, submenu_id, "/api/v1/menus/")


@app.get(
    "/api/v1/menus/{api_test_menu_id}/submenus/{submenu_id}/dishes/{dish_id}"
)
def show_concreate_dish(
    api_test_menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    dish: DishService = Depends(),
) -> dict:
    return dish.get(api_test_menu_id, submenu_id, dish_id, "/api/v1/menus/")


@app.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def update_existing_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    updated_dish: Dish,
    dish: DishService = Depends(),
) -> Dish:
    return dish.update(
        menu_id, submenu_id, dish_id, updated_dish, "/api/v1/menus/"
    )


@app.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_existing_dish(
    menu_id: uuid.UUID,
    submenu_id: uuid.UUID,
    dish_id: uuid.UUID,
    dish: DishService = Depends(),
) -> dict:
    return dish.delete(menu_id, submenu_id, dish_id, "/api/v1/menus/")
