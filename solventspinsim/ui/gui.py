import re
from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg

from solventspinsim.file.file_manager import FileManager
from solventspinsim.file.load import _load_array, _load_nmr_array, _load_spin_matrix
from solventspinsim.parse.settings import Settings
from solventspinsim.spin import Spin, _simulate_spin
from solventspinsim.theme.themes import _SUBPLOT_BORDER_COLORS, Theme

from .components.container import ChildWindow, Group, Window
from .components.input import Button, Checkbox, DragFloat, InputFloat, Separator, Text # InputText
from .components.menu import Menu, MenuBar, MenuItem
from .components.plot import Plot, PlotAxis, PlotLegend
from .fonts.font_handler import _try_load_font

# ---------------------------------------------------------------------------- #
#                                      GUI                                     #
# ---------------------------------------------------------------------------- #

class GUI:
    """
    Main application window.

    Layout:

        ┌─[MenuBar: File | Load | Save | Help]────────────────────────┐
        │ ┌─[main_plot] (tall, scrollable/pannable)──────────────────┐ │  ┌─[Settings panel]──┐
        │ │  Spectrum & Peaks                                         │ │  │ Field Strength    │
        │ │                                                           │ │  │ Points            │
        │ │                                                           │ │  │ Intensity         │
        │ │                                                           │ │  │ Half-Height Width │
        │ └───────────────────────────────────────────────────────────┘ │  │──────────────────│
        │ ┌─[subplot row]──────────────────────────────────────────── ┐ │  │ ☑ Enable Water   │
        │ │ [sub1] [sub2] [sub3] [sub4]                               │ │  │ Water Left Limit │
        │ └────────────────────────────────────────────────────────── ┘ │  │  ...             │
        └───────────────────────────────────────────────────────────────┘  └──────────────────┘
    """

    _SUBPLOT_COUNT = 4

    def __init__(self, title: str, settings: Settings) -> None:
        self._title: str = title
        self._settings: Settings = settings
        self._mgr: FileManager = FileManager()
        self._context_created: bool = False
        self._viewport_created: bool = False
        self._dark_mode: bool = settings.is_dark_mode()

    # ----------------------------- getters / setters ---------------------------- #
    def get_title(self) -> str:
        return self._title

    def get_settings(self) -> Settings:
        return self._settings

    def is_dark_mode(self) -> bool:
        return self._dark_mode

    def set_dark_mode(self, state: bool) -> None:
        self._dark_mode = state

    def get_file_manager(self) -> FileManager:
        return self._mgr

    # ----------------------------- internal helpers ----------------------------- #
    def _apply_theme(self) -> None:
        dpg.bind_theme(Theme.dark() if self._dark_mode else Theme.light())

    def _toggle_theme(self, sender: Any = None, app_data: Any = None, user_data: Any = None) -> None:
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    # --------------------------- file loading helpers --------------------------- #
    def _load_nmr_file(self, path: Path) -> None:
        """Load one NMR file, add to manager, refresh plots."""
        if not path.exists():
            print(f"[Warning] File not found: {path}")
            return

        ext = path.suffix.lower()
        try:
            if re.fullmatch(r"\.ft[1-9]", ext):
                data = _load_nmr_array(path)
            else:
                data = _load_array(path)
        except Exception as exc:
            print(f"[Error] Could not load {path}: {exc}")
            return

        self._mgr.add(path, data)
        self._refresh_all()

    def _load_nmr_file_dialog_callback(
        self,
        sender: Any,
        app_data: dict[str, Any],
        user_data: Any,
    ) -> None:
        selections: dict[str, str] = app_data.get("selections", {})
        for _, full_path in selections.items():
            self._load_nmr_file(Path(full_path))
        self._refresh_file_list()

    def _load_spin_file(self, path: Path) -> None:
        """Load one spin file, add to manager, refresh plots."""
        if not path.exists():
            print(f"[Warning] File not found: {path}")
            return
        try:
            data: Spin = _load_spin_matrix(path)
        except Exception as exc:
            print(f"[Error] Could not load {path}: {exc}")
            return
        
        self._mgr.add_spin(path, data)
        self._refresh_all()

    def _load_spin_file_dialog_callback(
        self,
        sender: Any,
        app_data: dict[str, Any],
        user_data: Any,
    ) -> None:
        selections: dict[str, str] = app_data.get("selections", {})
        for _, full_path in selections.items():
            self._load_spin_file(Path(full_path))
        self._refresh_file_list()

    # ------------------------------- plot refresh ------------------------------- #
    def _refresh_main_plot(self) -> None:
        """Delete and re-add all line series on the main plot."""
        # clear existing series
        if dpg.does_item_exist("main_plot_xaxis"):
            children = dpg.get_item_children("main_plot_xaxis", slot=1) or []
            for c in children:
                if dpg.does_item_exist(c):
                    dpg.delete_item(c)
        if dpg.does_item_exist("main_plot_yaxis"):
            children = dpg.get_item_children("main_plot_yaxis", slot=1) or []
            for c in children:
                if dpg.does_item_exist(c):
                    dpg.delete_item(c)

        for nf in self._mgr.list_files():
            if not nf.is_visible():
                continue
            series_tag = f"series_main_{nf.get_id()}"
            with dpg.theme() as series_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line,
                        nf.get_color(),
                        category=dpg.mvThemeCat_Plots,
                    )
            dpg.add_line_series(
                nf.get_x().tolist(),
                nf.get_y().tolist(),
                label=nf.get_label(),
                parent="main_plot_yaxis",
                tag=series_tag,
            )
            dpg.bind_item_theme(series_tag, series_theme)

        for sf in self._mgr.list_spins():
            if not sf.is_visible():
                continue
            spin_series_tag = f"spin_series_main_{sf.get_id()}"
            with dpg.theme() as series_theme:
                with dpg.theme_component(dpg.mvLineSeries):
                    dpg.add_theme_color(
                        dpg.mvPlotCol_Line,
                        sf.get_color(),
                        category=dpg.mvThemeCat_Plots,
                    )

            spin = sf.get_data() 
            spin.intensities = [ dpg.get_value("peak_intensity") ] * spin._nuclei_number
            spin.field_strength = dpg.get_value("field_strength")
            spin.nuclei_frequencies = spin._ppm_nuclei_frequencies

            spin_array = _simulate_spin(sf.get_data(), dpg.get_value("num_of_points"), dpg.get_value("hhw"))
            if spin_array is None:
                continue
            dpg.add_line_series(
                spin_array[0].tolist(),
                spin_array[1].tolist(),
                label=sf.get_label(),
                parent="main_plot_yaxis",
                tag=spin_series_tag,
            )
            dpg.bind_item_theme(spin_series_tag, series_theme)

    def _refresh_subplot_row(self) -> None:
        """Rebuild the bottom subplot row."""
        if not dpg.does_item_exist("subplot_row_group"):
            return
        dpg.delete_item("subplot_row_group", children_only=True)

        files = self._mgr.list_files()
        # We show up to _SUBPLOT_COUNT mini-plots; each corresponds to a loaded file
        n = min(len(files), self._SUBPLOT_COUNT)

        for i in range(self._SUBPLOT_COUNT):
            plot_tag = f"subplot_{i}"
            xax_tag  = f"subplot_{i}_xaxis"
            yax_tag  = f"subplot_{i}_yaxis"

            # Remove old plot if it exists
            if dpg.does_item_exist(plot_tag):
                dpg.delete_item(plot_tag)

            border_color = _SUBPLOT_BORDER_COLORS[i % len(_SUBPLOT_BORDER_COLORS)]

            # Each sub-plot gets its own themed container
            with dpg.theme() as sub_theme:
                with dpg.theme_component(dpg.mvChildWindow):
                    dpg.add_theme_color(dpg.mvThemeCol_Border, border_color)
                    dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 2)

            sub_cw_tag = f"subplot_cw_{i}"
            if dpg.does_item_exist(sub_cw_tag):
                dpg.delete_item(sub_cw_tag)

            dpg.add_child_window(
                tag=sub_cw_tag,
                width=200,
                height=-1,
                no_scrollbar=True,
                border=True,
                parent="subplot_row_group",
            )
            dpg.bind_item_theme(sub_cw_tag, sub_theme)

            dpg.add_plot(
                tag=plot_tag,
                width=-1,
                height=-1,
                no_title=True,
                no_menus=True,
                parent=sub_cw_tag,
            )
            dpg.add_plot_axis(dpg.mvXAxis, label="", tag=xax_tag,
                              no_tick_labels=True, parent=plot_tag)
            dpg.add_plot_axis(dpg.mvYAxis, label="", tag=yax_tag,
                              no_tick_labels=True, parent=plot_tag)

            if i < n:
                nf = files[i]
                series_tag = f"series_sub_{i}"
                with dpg.theme() as sub_series_theme:
                    with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_color(
                            dpg.mvPlotCol_Line,
                            nf.get_color(),
                            category=dpg.mvThemeCat_Plots,
                        )
                dpg.add_line_series(
                    nf.get_x().tolist(),
                    nf.get_y().tolist(),
                    parent=yax_tag,
                    tag=series_tag,
                )
                dpg.bind_item_theme(series_tag, sub_series_theme)

    def _refresh_file_list(self) -> None:
        """Rebuild the file list panel inside the settings area."""
        if not dpg.does_item_exist("file_list_panel"):
            return
        dpg.delete_item("file_list_panel", children_only=True)

        dpg.add_text("Loaded Files:", parent="file_list_panel")
        dpg.add_separator(parent="file_list_panel")

        files = self._mgr.list_files()
        spin_files = self._mgr.list_spins()
        if not files and not spin_files:
            dpg.add_text("(none)", parent="file_list_panel")
            return

        for nf in files:
            row_tag = f"filelist_row_{nf.get_id()}"
            with dpg.group(horizontal=True, parent="file_list_panel", tag=row_tag):
                r, g, b, _ = nf.get_color()
                dpg.add_color_button(
                    default_value=(r, g, b, 255),
                    width=14,
                    height=14,
                    no_tooltip=True,
                )
                dpg.add_checkbox(
                    label=nf.get_label(),
                    default_value=nf.is_visible(),
                    callback=self._on_visibility_toggle,
                    user_data=(nf.get_id(), "NMRFile"),
                )

        for sf in spin_files:
            row_tag = f"filelist_spin_row_{sf.get_id()}"
            with dpg.group(horizontal=True, parent="file_list_panel", tag=row_tag):
                r, g, b, _ = sf.get_color()
                dpg.add_color_button(
                    default_value=(r, g, b, 255),
                    width=14,
                    height=14,
                    no_tooltip=True,
                )
                dpg.add_checkbox(
                    label=sf.get_label(),
                    default_value=sf.is_visible(),
                    callback=self._on_visibility_toggle,
                    user_data=(sf.get_id(), "SpinFile"),
                )

    def _refresh_all(self) -> None:
        self._refresh_main_plot()
        self._refresh_subplot_row()
        self._refresh_file_list()

    # --------------------------------- callbacks -------------------------------- #
    def _on_visibility_toggle(
        self, sender: Any, app_data: bool, user_data: tuple[str, str]
    ) -> None:
        if user_data[1].lower() == "SpinFile".lower():
            f = self._mgr.get_spins(user_data[0])
        else:
            f = self._mgr.get_nmr(user_data[0])
        if f:
            f.set_visible(app_data)
            self._refresh_main_plot()

    # ---------------------------- window construction --------------------------- #
    def _build_nmr_file_dialog(self) -> None:
        with dpg.file_dialog(
            tag="nmr_file_dialog",
            directory_selector=False,
            show=False,
            callback=self._load_nmr_file_dialog_callback,
            width=720,
            height=420,
        ):
            dpg.add_file_extension(".ft1",  color=(100, 200, 100, 255))
            dpg.add_file_extension(".npy",  color=(100, 200, 100, 255))
            dpg.add_file_extension(".txt",  color=(200, 200, 100, 255))
            dpg.add_file_extension(".csv",  color=(200, 150, 100, 255))
            dpg.add_file_extension("",      color=(140, 140, 140, 255))

    def _build_spin_file_dialog(self) -> None:
        with dpg.file_dialog(
            tag="spin_file_dialog",
            directory_selector=False,
            show=False,
            callback=self._load_spin_file_dialog_callback,
            width=720,
            height=420,
        ):
            dpg.add_file_extension(".txt",  color=(200, 200, 100, 255))
            dpg.add_file_extension(".csv",  color=(200, 150, 100, 255))
            dpg.add_file_extension("",      color=(140, 140, 140, 255))

    def _render_main_window(self) -> None:
        # ---------------------------------- themes ---------------------------------- #
        Theme.light()
        Theme.dark()
        Theme.plot()
        self._apply_theme()

        # -------------------------------- file dialog ------------------------------- #
        self._build_nmr_file_dialog()
        self._build_spin_file_dialog()

        # ------------------------------ primary window ------------------------------ #
        main_window = Window(tag="main_window", label="Primary Window", no_scrollbar=True)

        menu_bar = MenuBar(tag="menu_bar")
        file_menu = Menu(label="File", tag="menu_file")
        file_menu.add_child(MenuItem(label="Exit", callback=lambda: dpg.stop_dearpygui()))
        load_menu = Menu(label="Load", tag="menu_load")
        load_menu.add_child(MenuItem(label="Load NMR File", callback=lambda: dpg.show_item("nmr_file_dialog")))
        load_menu.add_child(MenuItem(label="Load Spin File", callback=lambda: dpg.show_item("spin_file_dialog")))
        load_menu.add_child(MenuItem(label="Clear All", callback=self._on_clear_all))
        save_menu = Menu(label="Save", tag="menu_save")
        save_menu.add_child(MenuItem(label="Save Spin Matrix (TODO)"))
        view_menu = Menu(label="View", tag="menu_view")
        view_menu.add_child(MenuItem(label="Toggle Light/Dark Mode", callback=self._toggle_theme))
        help_menu = Menu(label="Help", tag="menu_help")
        help_menu.add_child(MenuItem(label="About 3S2R NMR"))

        menu_bar.add_menu(file_menu)
        menu_bar.add_menu(load_menu)
        menu_bar.add_menu(save_menu)
        menu_bar.add_menu(view_menu)
        menu_bar.add_menu(help_menu)
        main_window.add_child(menu_bar)

        body_group = Group(tag="body_group", horizontal=True)

        left_panel = ChildWindow(tag="left_panel", width=-320, height=-1, no_scrollbar=True, border=False)
        main_plot_window = ChildWindow(tag="main_plot_window", height=-180, no_scrollbar=True, border=False)
        main_plot = Plot(tag="main_plot", label="Spectrum & Peaks", width=-1, height=-1, pan_button=dpg.mvMouseButton_Left)
        main_plot.add_child(PlotLegend(tag="main_plot_legend"))
        main_plot.add_child(PlotAxis(dpg.mvXAxis, label="Hz", tag="main_plot_xaxis"))
        main_plot.add_child(PlotAxis(dpg.mvYAxis, label="Intensity", tag="main_plot_yaxis"))
        main_plot_window.add_child(main_plot)

        subplot_row_window = ChildWindow(tag="subplot_row_window", height=-1, horizontal_scrollbar=True, border=False)
        subplot_row_group = Group(horizontal=True, tag="subplot_row_group")
        subplot_row_window.add_child(subplot_row_group)
        left_panel.add_child(main_plot_window)
        left_panel.add_child(subplot_row_window)
        body_group.add_child(left_panel)

        settings_panel = ChildWindow(tag="settings_panel", width=310, height=-1, border=False)
        sim_settings_window = ChildWindow(tag="sim_settings_window", height=280, border=True)
        sim_settings_window.add_child(Text("Simulation Settings"))
        sim_settings_window.add_child(Separator())

        def _add_float_row(label: str, value_tag: str, default: float = 0.0, step: float = 1.0) -> None:
            row = Group()
            row.add_child(Text(label))
            row.add_child(
                InputFloat(
                    tag=value_tag,
                    default_value=default,
                    format="%.2f",
                    step=step,
                    step_fast=step * 10,
                    width=180,
                    callback=lambda: self._refresh_all(),
                )
            )
            sim_settings_window.add_child(row)

        _add_float_row("Field Strength", "field_strength", 500.0, 1.0)
        _add_float_row("Points", "num_of_points", 1000.0, 1.0)
        _add_float_row("Intensity", "peak_intensity", 1.0, 0.1)
        _add_float_row("Half-Height Width", "hhw", 1.0, 0.1)

        water_sim_window = ChildWindow(tag="water_sim_window", height=260, border=True)
        water_row = Group(horizontal=True)
        water_row.add_child(Checkbox(tag="enable_water_sim", default_value=False))
        water_row.add_child(Text("Enable Water Simulation"))
        water_sim_window.add_child(water_row)
        water_sim_window.add_child(Separator())

        def _add_drag_row(label: str, tag: str, default: float = 0.0) -> None:
            row = Group()
            row.add_child(Text(label))
            row.add_child(
                DragFloat(
                    tag=tag,
                    default_value=default,
                    format="%.2f",
                    speed=0.1,
                    width=230,
                    callback=lambda: self._refresh_all(),
                )
            )
            water_sim_window.add_child(row)

        _add_drag_row("Water Left Limit", "water_left_limit", 0.0)
        _add_drag_row("Water Right Limit", "water_right_limit", 1000.0)
        _add_drag_row("Water Frequency", "water_frequency", 0.0)
        _add_drag_row("Water Intensity", "water_intensity", 1.0)
        _add_drag_row("Water Half-Height Width", "water_hhw", 1.0)

        file_actions_window = ChildWindow(tag="file_actions_window", height=-1, border=True)
        file_list_panel = ChildWindow(tag="file_list_panel", height=-60, border=False)
        file_list_panel.add_child(Text("(no files loaded)"))
        file_actions_window.add_child(file_list_panel)
        file_actions_window.add_child(Separator())
        file_actions_window.add_child(Button(label="Optimize", width=-1, callback=self._on_optimize))

        settings_panel.add_child(sim_settings_window)
        settings_panel.add_child(water_sim_window)
        settings_panel.add_child(file_actions_window)
        body_group.add_child(settings_panel)
        main_window.add_child(body_group)
        main_window.submit()

        dpg.set_primary_window("main_window", True)

    def _on_clear_all(self, sender: Any = None, app_data: Any = None,
                      user_data: Any = None) -> None:
        self._mgr.clear()
        self._refresh_all()

    def _on_optimize(self, sender: Any = None, app_data: Any = None,
                     user_data: Any = None) -> None:
        # Placeholder — wire to your optimiser
        print("[Optimize] called (not yet implemented)")

    # ----------------------------- public functions ----------------------------- #
    def run(self, **viewport_kwargs: Any) -> None:
        dpg.create_context()
        self._context_created = True

        # Font (optional — comment out if Inter variable font not available)
        _try_load_font()

        dpg.create_viewport(title=self._title, decorated=True, **viewport_kwargs)
        dpg.setup_dearpygui()

        self._render_main_window()

        # Load any CLI-supplied files *after* the window is built
        for path in self._settings.get_cli_paths():
            self._load_nmr_file(path)

        # Initial subplot placeholder row
        self._refresh_subplot_row()

        dpg.show_viewport()
        dpg.start_dearpygui()

    def stop(self) -> None:
        if self._context_created:
            dpg.destroy_context()
        self._context_created = False
        self._viewport_created = False