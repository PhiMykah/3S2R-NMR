from typing import Any

import dearpygui.dearpygui as dpg

from .component import Component, _submit

# ---------------------------------------------------------------------------- #
#                             Container Components                             #
# ---------------------------------------------------------------------------- #


class Window(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._children: list[Component] = []

    def add_child(self, child: Component) -> None:
        self._children.append(child)

    def submit(self) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag", "label")}
        with dpg.window(tag=self.tag, label=self.label, **kwargs):
            for child in self._children:
                _submit(child)


class ChildWindow(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._children: list[Component] = []

    def add_child(self, child: Component) -> None:
        self._children.append(child)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag", "label")}
        if parent is not None:
            kwargs["parent"] = parent
        with dpg.child_window(tag=self.tag, label=self.label, **kwargs):
            for child in self._children:
                _submit(child)


class Group(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._children: list[Component] = []

    def add_child(self, child: Component) -> None:
        self._children.append(child)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag", "label")}
        if parent is not None:
            kwargs["parent"] = parent
        with dpg.group(**kwargs, tag=self.tag):
            for child in self._children:
                _submit(child)
