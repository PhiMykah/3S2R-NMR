from typing import Any, Callable

import dearpygui.dearpygui as dpg

# ---------------------------------------------------------------------------- #
#                            Component Base Classes                            #
# ---------------------------------------------------------------------------- #


class Component:
    """Wraps a dpg item with useful helper methods."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.label: str = kwargs.get("label", "")
        self.tag: int | str = kwargs.get("tag", dpg.generate_uuid())
        self.tags: list[int | str] = [self.tag]
        kwargs["tag"] = self.tag
        kwargs["label"] = self.label
        self._args = args
        self._kwargs = kwargs
        self.is_enabled: bool = kwargs.get("enabled", True)

    # ---------------------------- visibility / state ---------------------------- #
    def disable(self) -> None:
        dpg.disable_item(self.tag)
        self.is_enabled = False

    def enable(self) -> None:
        dpg.enable_item(self.tag)
        self.is_enabled = True

    def hide(self) -> None:
        dpg.hide_item(self.tag)

    def show(self) -> None:
        dpg.show_item(self.tag)

    def toggle_visibility(self) -> None:
        if dpg.is_item_shown(self.tag):
            self.hide()
        else:
            self.show()

    def bind_theme(self, theme_tag: int | str) -> None:
        dpg.bind_item_theme(self.tag, theme_tag)

    # ---------------------------------- getters --------------------------------- #
    def get_tag(self) -> int | str:
        return self.tag

    def get_label(self) -> str:
        return self.label


class iComponent(Component):
    """Component that owns a callback."""

    def set_callback(self, callback: Callable) -> None:
        dpg.set_item_callback(self.tag, callback)


# ---------------------------------------------------------------------------- #
#                            Recursive submit helper                           #
# ---------------------------------------------------------------------------- #


def _submit(component: Component, parent: int | str | None = None) -> None:
    """Recursively submit a component tree into the current DPG context."""
    if hasattr(component, "submit"):
        component.submit(parent=parent)  # type: ignore
