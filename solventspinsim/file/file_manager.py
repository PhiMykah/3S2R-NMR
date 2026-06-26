from pathlib import Path

import numpy as np

from solventspinsim.spin import Spin
from solventspinsim.theme.themes import _SERIES_COLORS
from .nmr import NMRFile
from .spin import SpinFile

# ---------------------------------------------------------------------------- #
#                                 File Manager                                 #
# ---------------------------------------------------------------------------- #


class FileManager:
    """Owns all loaded NMRFile and SpinFile objects."""

    def __init__(self) -> None:
        self._files: dict[str, NMRFile] = {}
        self._spins: dict[str, SpinFile] = {}
        self._color_index: int = 0

    def next_color(self) -> tuple[int, int, int, int]:
        color = _SERIES_COLORS[self._color_index % len(_SERIES_COLORS)]
        self._color_index += 1
        return color

    def add(self, path: Path, data: np.ndarray) -> NMRFile:
        nf = NMRFile(path, data, self.next_color())
        self._files[nf.get_id()] = nf
        return nf
    
    def add_spin(self, path: Path, data: Spin) -> SpinFile:
        spinmat = SpinFile(path, data, self.next_color())
        self._spins[spinmat.get_id()] = spinmat
        return spinmat

    def remove(self, file_id: str) -> None:
        self._files.pop(file_id, None)

    def remove_spin(self, spin_id: str) -> None:
        self._spins.pop(spin_id, None)

    def get(self, file_id: str) -> NMRFile | None:
        return self._files.get(file_id)
    
    def get_spins(self, spin_id: str) -> SpinFile | None:
        return self._spins.get(spin_id)
    
    def list_files(self) -> list[NMRFile]:
        return list(self._files.values())
    
    def list_spins(self) -> list[SpinFile]:
        return list(self._spins.values())
    
    def clear(self) -> None:
        self._files.clear()
        self._spins.clear()
        self._color_index = 0
