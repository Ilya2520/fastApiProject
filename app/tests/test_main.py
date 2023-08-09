# Standard Library
import uuid

from fastapi.testclient import TestClient

# Third Party
from app.database.database import DishModel, MenuModel, Session, SubmenuModel
from app.main import app

client = TestClient(app)


def clear_database():
    session = Session()
    session.query(DishModel).delete()
    session.query(SubmenuModel).delete()
    session.query(MenuModel).delete()
    session.commit()


# тесты для меню----------------------------------------------


def test_menu_get():
    clear_database()
    url = '/api/v1/menus/'
    response = client.get(url)
    assert response.json() == []


def test_menu_post():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    assert response.json()['title'] == 'menu1'
    assert response.json()['description'] == 'menu1 description'
    assert 'id' in response.json()


def test_menu_update():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    updated_menu = {
        'title': 'update menu1',
        'description': 'update menu1 description',
    }
    update_url = f'{url}{id}'
    response = client.patch(update_url, json=updated_menu)
    assert response.json()['title'] == 'update menu1'
    assert response.json()['description'] == 'update menu1 description'


def test_menu_update_error():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = '12fb8984-0000-44c2-a4ed-26738b6756e3'
    updated_menu = {
        'title': 'update menu1',
        'description': 'update menu1 description',
    }
    update_url = f'{url}{id}'
    response = client.patch(update_url, json=updated_menu)
    assert response.json() == {'detail': 'Menu not found'}


def test_menu_delete_error():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = '12fb8984-0000-44c2-a4ed-26738b6756e3'
    update_url = f'{url}{id}'
    response = client.delete(update_url)
    assert response.json() == {'message': 'error'}


def test_menu_delete():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    delete_url = f'{url}{id}'
    response = client.delete(delete_url)
    assert response.json()['message'] == 'successful'


# тесты для подменю------------------------------------------------------


def test_submenu_get():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    response = client.get(url)
    assert response.json() == []


def test_submenu_post():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    assert response.json()['title'] == 'submenu1'
    assert response.json()['description'] == 'submenu1 description'
    assert response.json()['id'] is not None


def test_submenu_update():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    submenu = {
        'title': 'update submenu1',
        'description': 'update submenu1 description',
    }
    url = f'{url}{id}'
    response = client.patch(url, json=submenu)
    assert response.json()['title'] == 'update submenu1'
    assert response.json()['description'] == 'update submenu1 description'


def test_submenu_delete():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    url = f'{url}{id}'
    response = client.delete(url)
    assert response.json()['message'] == 'successful delete'


# тесты для блюд------------------------------------------------------------


def test_dish_get():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    url = f'{url}{id}/dishes/'
    response = client.get(url)
    assert response.json() == []


def test_dish_post():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    dish = {
        'title': 'dish',
        'description': 'dish description',
        'price': '12.50',
    }
    url = f'{url}{id}/dishes/'
    response = client.post(url, json=dish)
    assert response.json()['title'] == 'dish'
    assert response.json()['description'] == 'dish description'
    assert response.json()['price'] == '12.50'


def test_dish_update():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    dish = {
        'title': 'dish',
        'description': 'dish description',
        'price': '12.50',
    }
    url = f'{url}{id}/dishes/'
    response = client.post(url, json=dish)
    id = response.json()['id']
    dish2 = {
        'title': 'update dish',
        'description': 'update dish description',
        'price': '1',
    }
    url = f'{url}{id}'
    response = client.patch(url, json=dish2)
    assert response.json()['title'] == 'update dish'
    assert response.json()['description'] == 'update dish description'
    assert response.json()['price'] == '1.00'


def test_dish_delete():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    id = response.json()['id']
    url = f'{url}{id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    id = response.json()['id']
    dish = {
        'title': 'dish',
        'description': 'dish description',
        'price': '12.50',
    }
    url = f'{url}{id}/dishes/'
    response = client.post(url, json=dish)
    id = response.json()['id']
    url = f'{url}/{id}'
    response = client.delete(url)
    assert response.json() == {'message': 'dish was deleted successful'}


# Функции для тестирования добавления и удаления блюд ------------------------


def menu_create():
    clear_database()
    url = 'api/v1/menus/'
    menu = {'title': 'menu1', 'description': 'menu1 description'}
    response = client.post(url, json=menu)
    assert response.json()['title'] == 'menu1'
    assert response.json()['description'] == 'menu1 description'
    return response.json()['id']


def submenu_create(menu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}/submenus/'
    submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
    response = client.post(url, json=submenu)
    assert response.json()['title'] == 'submenu1'
    assert response.json()['description'] == 'submenu1 description'
    return response.json()['id']


def dish_create(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish: str):
    url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'
    new_dish = {
        'title': dish,
        'description': f'{dish} description',
        'price': '11.5',
    }
    response = client.post(url, json=new_dish)
    assert response.json()['title'] == dish
    assert response.json()['description'] == f'{dish} description'
    assert response.json()['price'] == '11.50'
    return response.json()['id']


def menu_get(menu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}'
    response = client.get(url)
    assert response.json()['title'] == 'menu1'
    assert response.json()['description'] == 'menu1 description'
    assert response.json()['submenus_count'] == 1
    assert response.json()['dishes_count'] == 2
    assert response.json()['id'] is not None


def submenu_get(menu_id: uuid.UUID, submenu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}'
    response = client.get(url)
    assert response.json()['title'] == 'submenu1'
    assert response.json()['description'] == 'submenu1 description'
    assert response.json()['dishes_count'] == 2
    assert response.json()['id'] is not None


def delete_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}'
    response = client.delete(url)
    assert response.json() == {'message': 'successful delete'}


def show_submenus_after_delete(menu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}/submenus/'
    response = client.get(url)
    assert response.json() == []


def get_all_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'
    response = client.get(url)
    assert response.json() == []


def menu_get_after_delete(menu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}'
    response = client.get(url)
    assert response.json()['title'] == 'menu1'
    assert response.json()['description'] == 'menu1 description'
    assert response.json()['submenus_count'] == 0
    assert response.json()['dishes_count'] == 0
    assert response.json()['id'] is not None


def menu_delete(menu_id: uuid.UUID):
    url = f'api/v1/menus/{menu_id}'
    response = client.delete(url)
    assert response.json() == {'message': 'successful'}


def menu_get_after_delete_menu():
    url = 'api/v1/menus/'
    response = client.get(url)
    assert response.json() == []


def test_count_of_dishes():
    menu_id = menu_create()
    submenu_id = submenu_create(menu_id)
    dish_create(menu_id, submenu_id, 'dish1')
    dish_create(menu_id, submenu_id, 'dish2')
    menu_get(menu_id)
    submenu_get(menu_id, submenu_id)
    delete_submenu(menu_id, submenu_id)
    show_submenus_after_delete(menu_id)
    get_all_dish(menu_id, submenu_id)
    menu_get_after_delete(menu_id)
    menu_delete(menu_id)
    menu_get_after_delete_menu()
    clear_database()
