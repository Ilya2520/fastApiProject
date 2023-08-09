# Standard Library
import uuid

# Third Party
from fastapi import Depends

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

    def create(self, create_menu: Menu, path):
        self.service.delete_cache(path)
        return self.repository.create(create_menu, None, None)

    def get(self, menu_id: uuid.UUID, path: str):
        path, name = self.gets(path, menu_id)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get(menu_id, None, None)
        return self.service.get(path, name, cache, result)

    def get_all(self, path):
        path, name = self.gets_all(path)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get_all(None, None)
        return self.service.get_all(path, name, cache, result)

    def update(self, menu_id: uuid.UUID, updated_menu: Menu, path):
        self.service.delete_cache(path, menu_id)
        return self.repository.update(menu_id, None, None, updated_menu)

    def delete(self, menu_id: uuid.UUID, path):
        self.service.delete_cache(path, menu_id)
        return self.repository.delete(menu_id, None, None)
