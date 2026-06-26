from typing import Any

import dearpygui.dearpygui as dpg

from .component import iComponent


# ---------------------------------------------------------------------------- #
#                                Plot Components                               #
# ---------------------------------------------------------------------------- #


class Plot(iComponent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_plot(tag=self.tag, **kwargs)
