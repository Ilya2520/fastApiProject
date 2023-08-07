# Standard Library
import uuid

# Third Party
from fastapi import Depends

# Library
from app.models.models import Menu
from app.repositories.MenuRepository import MenuRepository
from app.services.RedisService import RedisService


class MenuService:
    def __init__(
        self,
        repository: MenuRepository = Depends(),
        redis_service: RedisService = Depends(),
    ):
        self.repository = repository
        self.service = redis_service

    def create(self, create_menu: Menu, path):
        self.service.delete_cache(path)
        return self.repository.create(create_menu, None, None)

    def get(self, menu_id: uuid.UUID, path: str):
        return self.service.get(path, menu_id, self.repository)

    def get_all(self, path):
        return self.service.get_all(path, self.repository)

    def update(self, menu_id: uuid.UUID, updated_menu: Menu, path):
        self.service.delete_cache(path, menu_id)
        return self.repository.update(menu_id, None, None, updated_menu)

    def delete(self, menu_id: uuid.UUID, path):
        self.service.delete_cache(path, menu_id)
        return self.repository.delete(menu_id, None, None)
