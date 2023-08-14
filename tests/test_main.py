# Standard Library
from app.main import app, clear_redis_on_startup
from app.database.database import MenuModel, async_session
import uuid

import httpx
import pytest
from sqlalchemy import select
import os
os.environ['TESTING'] = '1'

# Third Party


@pytest.fixture(scope='class')
async def http_client():
    async with httpx.AsyncClient(app=app, base_url='http://test') as client:
        yield client


URL = 'http://localchost/api/v1/menus/'


async def clear_database():
    async with async_session() as session:
        query = select(MenuModel)
        records = await session.execute(query)
        for record in records.scalars():
            await session.delete(record)
        await session.commit()


class Tests:

    @pytest.mark.asyncio
    async def test_get_menu(self, http_client):
        async for client in http_client:
            await clear_database()
            response = await client.get(URL)
            assert response.status_code == 200
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_create_new_menu(self, http_client):
        async for client in http_client:
            await clear_database()
            await clear_redis_on_startup()
            menu_data = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(URL, json=menu_data)
            assert response.status_code == 201
            menu = response.json()
            assert menu['title'] == 'menu1'
            assert menu['description'] == 'menu1 description'
            assert 'id' in menu

    @pytest.mark.asyncio
    async def test_menu_update(self, http_client):
        async for client in http_client:
            await clear_database()
            await clear_redis_on_startup()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            updated_menu = {
                'title': 'update menu1',
                'description': 'update menu1 description',
            }
            update_url = f'{url}{id}'
            response = await client.patch(update_url, json=updated_menu)
            assert response.json()['title'] == 'update menu1'
            assert response.json()['description'] == 'update menu1 description'

    @pytest.mark.asyncio
    async def test_menu_update_error(self, http_client):
        async for client in http_client:
            await clear_database()
            await clear_redis_on_startup()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = '12fb8984-0000-44c2-a4ed-26738b6756e3'
            updated_menu = {
                'title': 'update menu1',
                'description': 'update menu1 description',
            }
            update_url = f'{url}{id}'
            response = await client.patch(update_url, json=updated_menu)
            assert response.json() == {'detail': 'Menu not found'}

    @pytest.mark.asyncio
    async def test_menu_delete_error(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = client.post(url, json=menu)
            id = '12fb8984-0000-44c2-a4ed-26738b6756e3'
            update_url = f'{url}{id}'
            response = await client.delete(update_url)
            assert response.json() == {'message': 'error'}

    @pytest.mark.asyncio
    async def test_menu_delete(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            delete_url = f'{url}{id}'
            response = await client.delete(delete_url)
            assert response.json()['message'] == 'successful'

    # тесты для подменю------------------------------------------------------

    @pytest.mark.asyncio
    async def test_submenu_get(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            response = await client.get(url)
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_submenu_post(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            assert response.json()['title'] == 'submenu1'
            assert response.json()['description'] == 'submenu1 description'
            assert response.json()['id'] is not None

    @pytest.mark.asyncio
    async def test_submenu_update(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            submenu = {
                'title': 'update submenu1',
                'description': 'update submenu1 description',
            }
            url = f'{url}{id}'
            response = await client.patch(url, json=submenu)
            assert response.json()['title'] == 'update submenu1'
            assert response.json()['description'] == 'update submenu1 description'

    @pytest.mark.asyncio
    async def test_submenu_delete(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = await response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            url = f'{url}{id}'
            response = await client.delete(url)
            assert response.json()['message'] == 'successful delete'

    # тесты для блюд------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_dish_get(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            url = f'{url}{id}/dishes/'
            response = await client.get(url)
            assert response.json() == []

    @pytest.mark.asyncio
    async def test_dish_post(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            dish = {
                'title': 'dish',
                'description': 'dish description',
                'price': '12.50',
            }
            url = f'{url}{id}/dishes/'
            response = await client.post(url, json=dish)
            assert response.json()['title'] == 'dish'
            assert response.json()['description'] == 'dish description'
            assert response.json()['price'] == '12.50'

    @pytest.mark.asyncio
    async def test_dish_update(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            dish = {
                'title': 'dish',
                'description': 'dish description',
                'price': '12.50',
            }
            url = f'{url}{id}/dishes/'
            response = await client.post(url, json=dish)
            id = response.json()['id']
            dish2 = {
                'title': 'update dish',
                'description': 'update dish description',
                'price': '1',
            }
            url = f'{url}{id}'
            response = await client.patch(url, json=dish2)
            assert response.json()['title'] == 'update dish'
            assert response.json()['description'] == 'update dish description'
            assert response.json()['price'] == '1.00'

    @pytest.mark.asyncio
    async def test_dish_delete(self, http_client):
        async for client in http_client:
            await clear_database()
            url = 'api/v1/menus/'
            menu = {'title': 'menu1', 'description': 'menu1 description'}
            response = await client.post(url, json=menu)
            id = response.json()['id']
            url = f'{url}{id}/submenus/'
            submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
            response = await client.post(url, json=submenu)
            id = response.json()['id']
            dish = {
                'title': 'dish',
                'description': 'dish description',
                'price': '12.50',
            }
            url = f'{url}{id}/dishes/'
            response = await client.post(url, json=dish)
            id = response.json()['id']
            url = f'{url}/{id}'
            response = await client.delete(url)
            assert response.json() == {'message': 'dish was deleted successful'}

    # Функции для тестирования добавления и удаления блюд ------------------------

    async def menu_create(self, client):
        await clear_database()
        url = 'api/v1/menus/'
        menu = {'title': 'menu1', 'description': 'menu1 description'}
        response = await client.post(url, json=menu)
        assert response.json()['title'] == 'menu1'
        assert response.json()['description'] == 'menu1 description'
        return response.json()['id']

    async def submenu_create(self, client, menu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}/submenus/'
        submenu = {'title': 'submenu1', 'description': 'submenu1 description'}
        response = await client.post(url, json=submenu)
        assert response.json()['title'] == 'submenu1'
        assert response.json()['description'] == 'submenu1 description'
        return response.json()['id']

    async def dish_create(self, client, menu_id: uuid.UUID, submenu_id: uuid.UUID, dish: str):
        url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'
        new_dish = {
            'title': dish,
            'description': f'{dish} description',
            'price': '11.5',
        }
        response = await client.post(url, json=new_dish)
        assert response.json()['title'] == dish
        assert response.json()['description'] == f'{dish} description'
        assert response.json()['price'] == '11.50'
        return response.json()['id']

    async def menu_get(self, client, menu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}'
        response = await client.get(url)
        assert response.json()['title'] == 'menu1'
        assert response.json()['description'] == 'menu1 description'
        assert response.json()['submenus_count'] == 1
        assert response.json()['dishes_count'] == 2
        assert response.json()['id'] is not None

    async def submenu_get(self, client, menu_id: uuid.UUID, submenu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}'
        response = await client.get(url)
        assert response.json()['title'] == 'submenu1'
        assert response.json()['description'] == 'submenu1 description'
        assert response.json()['dishes_count'] == 2
        assert response.json()['id'] is not None

    async def delete_submenu(self, client, menu_id: uuid.UUID, submenu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}'
        response = await client.delete(url)
        assert response.json() == {'message': 'successful delete'}

    async def show_submenus_after_delete(self, client, menu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}/submenus/'
        response = await client.get(url)
        assert response.json() == []

    async def get_all_dish(self, client, menu_id: uuid.UUID, submenu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/'
        response = await client.get(url)
        assert response.json() == []

    async def menu_get_after_delete(self, client, menu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}'
        response = await client.get(url)
        assert response.json()['title'] == 'menu1'
        assert response.json()['description'] == 'menu1 description'
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0
        assert response.json()['id'] is not None

    async def menu_delete(self, client, menu_id: uuid.UUID):
        url = f'api/v1/menus/{menu_id}'
        response = await client.delete(url)
        assert response.json() == {'message': 'successful'}

    async def menu_get_after_delete_menu(self, client):
        url = 'api/v1/menus/'
        response = await client.get(url)
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_count_of_dishes(self, http_client):
        async for client in http_client:
            menu_id = await self.menu_create(client)
            submenu_id = await self.submenu_create(client, menu_id)
            await self.dish_create(client, menu_id, submenu_id, 'dish1')
            await self.dish_create(client, menu_id, submenu_id, 'dish2')
            await self.menu_get(client, menu_id)
            await self.submenu_get(client, menu_id, submenu_id)
            await self.delete_submenu(client, menu_id, submenu_id)
            await self.show_submenus_after_delete(client, menu_id)
            await self.get_all_dish(client, menu_id, submenu_id)
            await self.menu_get_after_delete(client, menu_id)
            await self.menu_delete(client, menu_id)
            await self.menu_get_after_delete_menu(client)
            await clear_database()
