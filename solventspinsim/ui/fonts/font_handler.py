from pathlib import Path
import dearpygui.dearpygui as dpg

# ---------------------------------------------------------------------------- #
#                                  Font Loader                                 #
# ---------------------------------------------------------------------------- #

def _try_load_font() -> None:
    """Load Inter variable font if present next to this script."""
    font_path = Path(__file__).parent / "inter-variable.ttf"
    if font_path.exists():
        with dpg.font_registry():
            fnt = dpg.add_font(str(font_path), 18)
        dpg.bind_font(fnt)
    dpg.set_global_font_scale(1.0)
