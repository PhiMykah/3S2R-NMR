from pathlib import Path

# ---------------------------------------------------------------------------- #
#                              Settings Dataclass                              #
# ---------------------------------------------------------------------------- #


class Settings:
    """Holds runtime settings parsed from CLI args."""

    def __init__(self, cli_paths: list[Path] | None = None) -> None:
        self._cli_paths: list[Path] = cli_paths or []
        self._dark_mode: bool = True  # default

    def get_cli_paths(self) -> list[Path]:
        return self._cli_paths

    def set_cli_paths(self, paths: list[Path]) -> None:
        self._cli_paths = paths

    def is_dark_mode(self) -> bool:
        return self._dark_mode

    def set_dark_mode(self, state: bool) -> None:
        self._dark_mode = state
