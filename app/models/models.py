# Standard Library
from decimal import Decimal
from typing import List, Optional

# Third Party
from pydantic import UUID4, BaseModel


class Dish(BaseModel):
    title: str
    description: str
    price: Decimal


class Submenu(BaseModel):
    title: str
    description: str
    dishes: Optional[List[Dish]] = []
    dishes_count: int = 0


class Menu(BaseModel):
    title: str
    description: str
    submenus: Optional[List[Submenu]] = []
    dishes_count: int = 0
    submenus_count: int = 0


class MenuUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


class UpdatedMenu(BaseModel):
    id: UUID4
    title: str
    description: str


class SubmenuUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


class DishUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[str]
