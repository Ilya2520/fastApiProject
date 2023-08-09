# Standard Library
from decimal import Decimal

# Third Party
from pydantic import UUID4, BaseModel


class Dish(BaseModel):
    title: str
    description: str
    price: Decimal


class Submenu(BaseModel):
    title: str
    description: str
    dishes: list[Dish] | None = []
    dishes_count: int = 0


class Menu(BaseModel):
    title: str
    description: str
    submenus: list[Submenu] | None = []
    dishes_count: int = 0
    submenus_count: int = 0


class MenuUpdate(BaseModel):
    title: str | None
    description: str | None


class UpdatedMenu(BaseModel):
    id: UUID4
    title: str
    description: str


class SubmenuUpdate(BaseModel):
    title: str | None
    description: str | None


class DishUpdate(BaseModel):
    title: str | None
    description: str | None
    price: str | None
