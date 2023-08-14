# Standard Library
from decimal import Decimal

# Third Party
from pydantic import BaseModel


class Model(BaseModel):
    title: str
    description: str


class Dish(Model):
    price: Decimal


class Submenu(Model):
    dishes: list[Dish] | None = []
    dishes_count: int = 0


class Menu(Model):
    submenus: list[Submenu] | None = []
    dishes_count: int = 0
    submenus_count: int = 0
