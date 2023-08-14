# Standard Library

import json
import uuid

# Third Party
import aioredis  # type: ignore


async def cache_miss(result,
                     name: str):
    result['id'] = str(result['id'])
    if name != 'none':
        for subresult in result[name]:
            subresult['id'] = str(subresult['id'])
    return result


async def cache_miss_all(results,
                         name):
    result = []
    for res in results:
        res['id'] = str(res['id'])
        if name != 'none':
            for subresult in res[name]:
                subresult['id'] = str(subresult['id'])
        result.append(res)
    return result, results


class RedisService:
    def __init__(self):
        self.redis = aioredis.from_url(
            'redis://redis:6379',
            decode_responses=True)

    async def delete_cache(
            self,
            path,
            menu_id: uuid.UUID | None = None,
            submenu_id: uuid.UUID | None = None,
            dish_id: uuid.UUID | None = None,
    ):
        path_to_menu = f'{path}{menu_id}'
        path_submenus = f'{path_to_menu}/submenus/'
        path_to_submenu = f'{path_submenus}{submenu_id}'
        path_to_dishes = f'{path_to_submenu}/dishes/'
        path_to_dish = f'{path_to_dishes}{dish_id}'
        await self.delete_concreate_cache(path)
        await self.delete_concreate_cache(path_to_menu)
        await self.delete_concreate_cache(path_submenus)
        await self.delete_concreate_cache(path_to_submenu)
        await self.delete_concreate_cache(path_to_dishes)
        await self.delete_concreate_cache(path_to_dish)

    async def delete_concreate_cache(self, path):
        cache = await self.redis.get(path)
        if cache:
            await self.redis.delete(path)

    async def get(
            self,
            path: str,
            name: str,
            cache,
            result: dict | None = None
    ):
        if cache:
            print('cache hit')
            cached_menu = json.loads(cache)
            cached_menu['id'] = uuid.UUID(cached_menu['id'])
            return cached_menu
        else:
            print('cache miss')
            result = await cache_miss(result, name)
            await self.redis.set(path, json.dumps(result))
            await self.redis.expire(path, 1000)
            return result

    async def get_all(
            self,
            path: str,
            name,
            cache,
            result_all: dict | None = None
    ):
        if cache:
            print('cache hit')
            print(cache)
            js = json.loads(cache)
            print(js)
            return js
        else:
            print('cache miss')
            result, results = await cache_miss_all(result_all, name)
            await self.redis.set(path, json.dumps(result))
            await self.redis.expire(path, 1000)
            return results

    async def save_excel_data(self, data, counts):
        json_data = json.dumps(data)
        json_data_counts = json.dumps(counts)
        await self.redis.set('excel_data', json_data)
        await self.redis.set('excel_data_counts', json_data_counts)

    async def get_excel_data(self):
        json_data = await self.redis.get('excel_data')
        json_data1 = await self.redis.get('excel_data_counts')
        if json_data:
            return json.loads(json_data), json.loads(json_data1)
        return None, None
    #
    # def update(self,
    #            path: str,
    #            repository: Repository,
    #            name,
    #            model: BaseModel,
    #            menu_id: uuid.UUID | None = None,
    #            submenu_id: uuid.UUID | None = None,
    #            dish_id: uuid.UUID | None = None):
    #     cache = self.redis.get(path)
    #     result = json.loads(cache)
    #     if dish_id and model.price:
    #         result["price"] = model.price
    #     if model.description:
    #         result["description"] = model.description
    #     if model.title:
    #         result["title"] = model.title
    #     self.redis.set(path, json.dumps(result))
    #     self.redis.expire(path, 1000)
    #     repository.update(menu_id, submenu_id, dish_id, model)
