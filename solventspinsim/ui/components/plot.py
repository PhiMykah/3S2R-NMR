from typing import Any

import dearpygui.dearpygui as dpg

from .component import Component, _submit, iComponent


# ---------------------------------------------------------------------------- #
#                                Plot Components                               #
# ---------------------------------------------------------------------------- #


class Plot(iComponent):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._children: list[Component] = []

    def add_child(self, child: Component) -> None:
        self._children.append(child)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        with dpg.plot(tag=self.tag, **kwargs):
            for child in self._children:
                _submit(child)


class PlotLegend(Component):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def submit(self, parent: int | str | None = None) -> None:
        kwargs: dict[str, Any] = {"tag": self.tag}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_plot_legend(**kwargs)


class PlotAxis(Component):
    def __init__(self, axis_type: int, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._axis_type = axis_type

    def submit(self, parent: int | str | None = None) -> None:
        kwargs = {k: v for k, v in self._kwargs.items() if k not in ("tag",)}
        if parent is not None:
            kwargs["parent"] = parent
        dpg.add_plot_axis(self._axis_type, tag=self.tag, **kwargs)
