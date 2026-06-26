from typing import Any

import dearpygui.dearpygui as dpg

from .component import Component, iComponent

# ---------------------------------------------------------------------------- #
#                            Leaf / Input Components                           #
# ---------------------------------------------------------------------------- #


class Text(Component):
    def __init__(self, value: str = "", *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._value = value

    def submit(self, parent: int | str | None = None) -> None:
        kwargs: dict[str, Any] = {"tag": self.tag}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_text(self._value, **kwargs)


class Button(iComponent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_button(tag=self.tag, **kwargs)


class Checkbox(iComponent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_checkbox(tag=self.tag, **kwargs)


class Separator(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs: dict[str, Any] = {"tag": self.tag}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_separator(**kwargs)
