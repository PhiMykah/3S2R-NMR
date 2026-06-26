from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------- #
#                                NMR File Record                               #
# ---------------------------------------------------------------------------- #


class NMRFile:
    """Holds a loaded data array and its display metadata."""

    _id_counter: int = 0

    def __init__(
        self, path: Path, data: np.ndarray, color: tuple[int, int, int, int]
    ) -> None:
        NMRFile._id_counter += 1
        self._id: str = f"nmrfile_{NMRFile._id_counter}"
        self._path: Path = path
        self._data: np.ndarray = data  # shape (2, N)
        self._color: tuple[int, int, int, int] = color
        self._visible: bool = True
        self._label: str = path.stem

    # ----------------------------- getters / setters ---------------------------- #
    def get_id(self) -> str:
        return self._id

    def get_path(self) -> Path:
        return self._path

    def get_data(self) -> np.ndarray:
        return self._data

    def get_color(self) -> tuple[int, int, int, int]:
        return self._color

    def get_label(self) -> str:
        return self._label

    def set_label(self, label: str) -> None:
        self._label = label

    def is_visible(self) -> bool:
        return self._visible

    def set_visible(self, state: bool) -> None:
        self._visible = state

    def toggle_visible(self) -> None:
        self._visible = not self._visible

    # --------------------- dimension getters for convenience -------------------- #
    def get_x(self) -> np.ndarray:
        return self._data[0]

    def get_y(self) -> np.ndarray:
        return self._data[1]
