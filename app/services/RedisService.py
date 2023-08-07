# Standard Library
import json
import uuid
from typing import Union

# Third Party
import redis  # type: ignore

# Library
from app.repositories.Repository import Repository


def get_name_all(
    menu_id: uuid.UUID, submenu_id: Union[uuid.UUID, None] = None
):
    if submenu_id:
        name = "none"
    elif menu_id:
        name = "dishes"
    else:
        name = "submenus"
    return name


def get_path_all(
    path: str,
    menu_id: Union[uuid.UUID, None] = None,
    submenu_id: Union[uuid.UUID, None] = None,
):
    if submenu_id:
        path = f"{path}{menu_id}/submenus/{submenu_id}/dishes/"
    elif menu_id:
        path = f"{path}{menu_id}/submenus/"
    else:
        path = f"{path}"
    return path


def get_name(
    submenu_id: Union[uuid.UUID, None] = None,
    dish_id: Union[uuid.UUID, None] = None,
):
    if dish_id:
        name = "none"
    elif submenu_id:
        name = "dishes"
    else:
        name = "submenus"
    return name


def get_path(
    path: str,
    menu_id: uuid.UUID,
    submenu_id: Union[uuid.UUID, None] = None,
    dish_id: Union[uuid.UUID, None] = None,
):
    if dish_id:
        path = f"{path}{menu_id}/submenus/{submenu_id}/dishes/{dish_id}"
    elif submenu_id:
        path = f"{path}{menu_id}/submenus/{submenu_id}"
    else:
        path = f"{path}{menu_id}"
    return path


class RedisService:
    def __init__(self):
        self.redis = redis.Redis(
            host="redis", port=6379, decode_responses=True
        )

    def delete_cache(
        self,
        path,
        menu_id: Union[uuid.UUID, None] = None,
        submenu_id: Union[uuid.UUID, None] = None,
        dish_id: Union[uuid.UUID, None] = None,
    ):
        path_to_menu = f"{path}{menu_id}"
        path_submenus = f"{path_to_menu}/submenus/"
        path_to_submenu = f"{path_submenus}{submenu_id}"
        path_to_dishes = f"{path_to_submenu}/dishes/"
        path_to_dish = f"{path_to_dishes}{dish_id}"
        self.delete_concreate_cache(path)
        self.delete_concreate_cache(path_to_menu)
        self.delete_concreate_cache(path_submenus)
        self.delete_concreate_cache(path_to_submenu)
        self.delete_concreate_cache(path_to_dishes)
        self.delete_concreate_cache(path_to_dish)

    def delete_concreate_cache(self, path):
        cache = self.redis.get(path)
        print(path)
        print(cache)
        if cache:
            self.redis.delete(path)

    def get_something(
        self,
        path: str,
        menu_id: uuid.UUID,
        repository: Repository,
        name: str,
        submenu_id: Union[uuid.UUID, None] = None,
        dish_id: Union[uuid.UUID, None] = None,
    ):
        cache = self.redis.get(path)
        if cache:
            print("cache hit")
            cached_menu = json.loads(cache)
            cached_menu["id"] = uuid.UUID(cached_menu["id"])
            return cached_menu
        else:
            print("cache miss")
            if dish_id:
                result = repository.get(menu_id, submenu_id, dish_id)
            elif submenu_id:
                result = repository.get(menu_id, submenu_id, None)
            else:
                result = repository.get(menu_id, None, None)
            result["id"] = str(result["id"])
            if name != "none":
                for subresult in result[name]:
                    subresult["id"] = str(subresult["id"])
            self.redis.set(path, json.dumps(result))
            self.redis.expire(path, 1000)
            return result

    def get_all_by_path(
        self,
        path: str,
        repository: Repository,
        name,
        menu_id: Union[uuid.UUID, None] = None,
        submenu_id: Union[uuid.UUID, None] = None,
    ):
        cache = self.redis.get(path)
        if cache:
            print("cache hit")
            print(cache)
            js = json.loads(cache)
            print(js)
            return js
        else:
            print("cache miss")
            if submenu_id:
                results = repository.get_all(menu_id, submenu_id)
            elif menu_id:
                results = repository.get_all(menu_id, None)
            else:
                results = repository.get_all(None, None)
            result = []
            for res in results:
                res["id"] = str(res["id"])
                if name != "none":
                    for subresult in res[name]:
                        subresult["id"] = str(subresult["id"])
                result.append(res)
            self.redis.set(path, json.dumps(result))
            self.redis.expire(path, 1000)
            return results

    def get(
        self,
        path,
        menu_id: uuid.UUID,
        repository: Repository,
        submenu_id: Union[uuid.UUID, None] = None,
        dish_id: Union[uuid.UUID, None] = None,
    ):
        path = get_path(path, menu_id, submenu_id, dish_id)
        name = get_name(submenu_id, dish_id)
        return self.get_something(
            path, menu_id, repository, name, submenu_id, dish_id
        )

    def get_all(
        self,
        path,
        repository: Repository,
        menu_id: Union[uuid.UUID, None] = None,
        submenu_id: Union[uuid.UUID, None] = None,
    ):
        path = get_path_all(path, menu_id, submenu_id)
        print(path)
        name = get_name_all(menu_id, submenu_id)  # type: ignore
        return self.get_all_by_path(
            path, repository, name, menu_id, submenu_id
        )
