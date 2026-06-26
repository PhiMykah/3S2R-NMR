import dearpygui.dearpygui as dpg

# ---------------------------------------------------------------------------- #
#                   Color palette for successive file series                   #
# ---------------------------------------------------------------------------- #

_SERIES_COLORS: list[tuple[int, int, int, int]] = [
    (100, 180, 255, 255),  # blue
    (100, 220, 140, 255),  # green
    (255, 160, 100, 255),  # orange
    (200, 120, 220, 255),  # purple
    (255, 220, 80, 255),  # yellow
    (100, 220, 220, 255),  # cyan
    (255, 100, 130, 255),  # red-pink
]

_SUBPLOT_BORDER_COLORS: list[tuple[int, int, int, int]] = [
    (220, 80, 80, 200),  # pink/red
    (80, 200, 80, 200),  # green
    (80, 80, 220, 200),  # blue
    (200, 200, 80, 200),  # yellow
]

# ---------------------------------------------------------------------------- #
#                                 Theme Helper                                 #
# ---------------------------------------------------------------------------- #


class Theme:
    """Creates and caches DPG themes."""

    _light_tag: int | str | None = None
    _dark_tag: int | str | None = None
    _plot_tag: int | str | None = None

    @classmethod
    def light(cls) -> int | str:
        if cls._light_tag is not None:
            return cls._light_tag
        with dpg.theme() as t:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (240, 240, 240, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (225, 225, 225, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (20, 20, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 180, 180, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (160, 160, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (130, 130, 210, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (235, 235, 235, 255))
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (210, 210, 210, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (180, 200, 230, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (160, 190, 220, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (210, 210, 210, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (160, 160, 160, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (180, 180, 180, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (160, 160, 200, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
        cls._light_tag = t
        return t

    @classmethod
    def dark(cls) -> int | str:
        if cls._dark_tag is not None:
            return cls._dark_tag
        with dpg.theme() as t:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (40, 40, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 110, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 140, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 50, 255))
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (35, 35, 35, 255))
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (30, 30, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (60, 80, 120, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (70, 90, 130, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (30, 30, 30, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (80, 80, 80, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (20, 20, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (40, 40, 80, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
        cls._dark_tag = t
        return t

    @classmethod
    def plot(cls) -> int | str:
        """Theme that removes the plot background so the ChildWindow bg shows."""
        if cls._plot_tag is not None:
            return cls._plot_tag
        with dpg.theme() as t:
            with dpg.theme_component(dpg.mvPlot):
                dpg.add_theme_color(
                    dpg.mvPlotCol_FrameBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots
                )
        cls._plot_tag = t
        return t
