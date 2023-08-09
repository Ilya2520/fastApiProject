import uuid


class Service:
    def __init__(self):
        pass

    def get_name_all(self,
                     menu_id: uuid.UUID | None = None, submenu_id: uuid.UUID | None = None
                     ):
        if submenu_id:
            name = 'none'
        elif menu_id:
            name = 'dishes'
        else:
            name = 'submenus'
        return name

    def get_path_all(self,
                     path: str,
                     menu_id: uuid.UUID | None = None,
                     submenu_id: uuid.UUID | None = None,
                     ):
        if submenu_id:
            path = f'{path}{menu_id}/submenus/{submenu_id}/dishes/'
        elif menu_id:
            path = f'{path}{menu_id}/submenus/'
        else:
            path = f'{path}'
        return path

    def get_name(self,
                 submenu_id: uuid.UUID | None = None,
                 dish_id: uuid.UUID | None = None,
                 ):
        if dish_id:
            name = 'none'
        elif submenu_id:
            name = 'dishes'
        else:
            name = 'submenus'
        return name

    def get_path(self,
                 path: str,
                 menu_id: uuid.UUID,
                 submenu_id: uuid.UUID | None = None,
                 dish_id: uuid.UUID | None = None,
                 ):
        if dish_id:
            path = f'{path}{menu_id}/submenus/{submenu_id}/dishes/{dish_id}'
        elif submenu_id:
            path = f'{path}{menu_id}/submenus/{submenu_id}'
        else:
            path = f'{path}{menu_id}'
        return path

    def gets(
            self,
            path,
            menu_id: uuid.UUID,
            submenu_id: uuid.UUID | None = None,
            dish_id: uuid.UUID | None = None
    ):
        path = self.get_path(path, menu_id, submenu_id, dish_id)
        name = self.get_name(submenu_id, dish_id)
        return path, name

    def gets_all(
            self,
            path,
            menu_id: uuid.UUID | None = None,
            submenu_id: uuid.UUID | None = None,
    ):
        path = self.get_path_all(path, menu_id, submenu_id)
        name = self.get_name_all(menu_id, submenu_id)  # type: ignore
        return path, name
