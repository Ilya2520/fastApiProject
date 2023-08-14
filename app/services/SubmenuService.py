# Standard Library
import uuid

# Third Party
from fastapi import Depends, BackgroundTasks

# Library
from app.models.models import Submenu
from app.repositories.SubmenuRepository import SubmenuRepository
from app.services.RedisService import RedisService
from app.services.Service import Service


class SubmenuService(Service):
    def __init__(self, repository: SubmenuRepository = Depends(), redis_service: RedisService = Depends()):
        super().__init__()
        self.repository = repository
        self.service = redis_service

    async def create(self, menu_id: uuid.UUID, submenu_new: Submenu, path: str):
        await self.service.delete_cache(path, menu_id)
        return await self.repository.create(submenu_new, menu_id, None)

    async def get_all(self, menu_id: uuid.UUID, path: str):
        path, name = await self.gets_all(path, menu_id)
        cache = await self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = await self.repository.get_all(menu_id, None)
        return await self.service.get_all(path, name, cache, result)

    async def get(self, menu_id: uuid.UUID, submenu_id: uuid.UUID, path: str):
        path, name = await self.gets(path, menu_id, submenu_id)
        cache = await self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = await self.repository.get(menu_id, submenu_id, None)
        return await self.service.get(path, name, cache, result)

    async def update(
            self,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            updated_submenu: Submenu,
            path: str,
            background_tasks: BackgroundTasks
    ):

        background_tasks.add_task(self.service.delete_cache, path, menu_id, submenu_id, None)
        return await self.repository.update(
            menu_id, submenu_id, None, updated_submenu
        )

    async def delete(self, menu_id: uuid.UUID, submenu_id: uuid.UUID, path: str, background_tasks: BackgroundTasks):
        background_tasks.add_task(self.service.delete_cache, path, menu_id, submenu_id, None)
        return await self.repository.delete(menu_id, submenu_id, None)
