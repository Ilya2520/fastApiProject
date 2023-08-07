# Standard Library
import uuid

# Third Party
from fastapi import Depends

# Library
from app.models.models import Submenu
from app.repositories.SubmenuRepository import SubmenuRepository
from app.services.RedisService import RedisService


class SubmenuService:
    def __init__(
        self,
        repository: SubmenuRepository = Depends(),
        redis_service: RedisService = Depends(),
    ):
        self.repository = repository
        self.service = redis_service

    def create(self, menu_id: uuid.UUID, submenu_new: Submenu, path: str):
        self.service.delete_cache(path, menu_id)
        return self.repository.create(submenu_new, menu_id, None)

    def get_all(self, menu_id: uuid.UUID, path: str):
        return self.service.get_all(path, self.repository, menu_id)

    def get(self, menu_id: uuid.UUID, submenu_id: uuid.UUID, path: str):
        return self.service.get(path, menu_id, self.repository, submenu_id)

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
