# Standard Library
import uuid

# Third Party
from fastapi import Depends, BackgroundTasks

# Library
from app.models.models import Menu
from app.repositories.MenuRepository import MenuRepository
from app.services.RedisService import RedisService
from app.services.Service import Service


class MenuService(Service):
    def __init__(self, repository: MenuRepository = Depends(), redis_service: RedisService = Depends()):
        super().__init__()
        self.repository = repository
        self.service = redis_service

    async def create(self, create_menu: Menu, path):
        await self.service.delete_cache(path)
        return await self.repository.create(create_menu, None, None)

    async def get(self, menu_id: uuid.UUID, path: str):
        path, name = await self.gets(path, menu_id)
        cache = await self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = await self.repository.get(menu_id, None, None)
        return await self.service.get(path, name, cache, result)

    async def get_all(self, path):
        path, name = await self.gets_all(path)
        cache = await self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = await self.repository.get_all(None, None)
        print(path, name, cache, result)
        return await self.service.get_all(path, name, cache, result)

    async def update(self, menu_id: uuid.UUID, updated_menu: Menu, path, background_tasks: BackgroundTasks):
        background_tasks.add_task(self.service.delete_cache, path, menu_id, None, None)
        return await self.repository.update(menu_id, None, None, updated_menu)

    async def delete(self, menu_id: uuid.UUID, path, background_tasks: BackgroundTasks):
        background_tasks.add_task(self.service.delete_cache, path, menu_id, None, None)
        return await self.repository.delete(menu_id, None, None)

    async def menus(self):
        return await self.repository.get_all_menus()
