# Standard Library
import uuid

# Third Party
from fastapi import Depends

# Library
from app.models.models import Dish
from app.repositories.DishRepository import DishRepository
from app.services.RedisService import RedisService
from app.services.Service import Service


class DishService(Service):
    def __init__(self, repository: DishRepository = Depends(), redis_service: RedisService = Depends()):
        super().__init__()
        self.repository = repository
        self.service = redis_service

    def create(
            self,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            dish_new: Dish,
            path: str,
    ):
        self.service.delete_cache(path, menu_id, submenu_id)
        return self.repository.create(dish_new, menu_id, submenu_id)

    def get_all(
            self, api_test_menu_id: uuid.UUID, submenu_id: uuid.UUID, path
    ):
        path, name = self.gets_all(path, api_test_menu_id, submenu_id)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get_all(api_test_menu_id, submenu_id)
        return self.service.get_all(path, name, cache, result)

    def get(
            self,
            api_test_menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            dish_id: uuid.UUID,
            path,
    ):
        path, name = self.gets(path, api_test_menu_id, submenu_id, dish_id)
        cache = self.service.redis.get(path)
        if cache:
            result = None
        else:
            result = self.repository.get(api_test_menu_id, submenu_id, dish_id)
        return self.service.get(path, name, cache, result)

    def update(
            self,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            dish_id: uuid.UUID,
            updated_dish: Dish,
            path,
    ):
        self.service.delete_cache(path, menu_id, submenu_id, dish_id)
        return self.repository.update(
            menu_id, submenu_id, dish_id, updated_dish
        )

    def delete(
            self,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID,
            dish_id: uuid.UUID,
            path: str,
    ):
        self.service.delete_cache(path, menu_id, submenu_id, dish_id)
        return self.repository.delete(menu_id, submenu_id, dish_id)
