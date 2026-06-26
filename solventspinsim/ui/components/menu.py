from typing import Any

import dearpygui.dearpygui as dpg

from .component import Component, _submit, iComponent

# ---------------------------------------------------------------------------- #
#                                Menu Components                               #
# ---------------------------------------------------------------------------- #


class MenuItem(iComponent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_menu_item(tag=self.tag, **kwargs)


class Menu(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._children: list[Component] = []

    def add_child(self, child: Component) -> None:
        self._children.append(child)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        with dpg.menu(tag=self.tag, **kwargs):
            for child in self._children:
                _submit(child)


class MenuBar(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._menus: list[Component] = []

    def add_menu(self, menu: Component) -> None:
        self._menus.append(menu)

    def submit(self, parent: int | str | None = None) -> None:
        with dpg.menu_bar(tag=self.tag):
            for menu in self._menus:
                _submit(menu)
