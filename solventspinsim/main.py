from __future__ import annotations

from sys import argv

from solventspinsim.parse import parse_args, Settings
from solventspinsim.ui import GUI

# ---------------------------------------------------------------------------- #
#                                  Entry Point                                 #
# ---------------------------------------------------------------------------- #


def entry(args: list[str] = argv[1:]) -> None:
    settings = Settings(cli_paths=parse_args(args))
    gui = GUI(title="3S2R NMR", settings=settings)
    gui.run(width=1400, height=780, clear_color=(0, 0, 0, 0))
    gui.stop()


if __name__ == "__main__":
    entry()
