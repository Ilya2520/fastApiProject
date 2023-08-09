# Standard Library
import uuid

# Third Party
from fastapi import Depends

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

    def create(self, menu_id: uuid.UUID, submenu_new: Submenu, path: str):
        self.service.delete_cache(path, menu_id)
        return self.repository.create(submenu_new, menu_id, None)

    def get_all(self, menu_id: uuid.UUID, path: str):
        path, name = self.gets_all(path, menu_id)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get_all(menu_id, None)
        return self.service.get_all(path, name, cache, result)

    def get(self, menu_id: uuid.UUID, submenu_id: uuid.UUID, path: str):
        path, name = self.gets(path, menu_id, submenu_id)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get(menu_id, submenu_id, None)
        return self.service.get(path, name, cache, result)

    def update(
            self,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            updated_submenu: Submenu,
            path: str,
    ):
        self.service.delete_cache(path, menu_id, submenu_id)
        return self.repository.update(
            menu_id, submenu_id, None, updated_submenu
        )

    def delete(self, menu_id: uuid.UUID, submenu_id: uuid.UUID, path: str):
        self.service.delete_cache(path, menu_id, submenu_id)
        return self.repository.delete(menu_id, submenu_id, None)
