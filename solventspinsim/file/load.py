from pathlib import Path

import numpy as np
from nmrPype import DataFrame
from solventspinsim.spin import _get_spin_matrix, Spin

# ---------------------------------------------------------------------------- #
#                               NMR File Loading                               #
# ---------------------------------------------------------------------------- #

def _load_nmr_array(file: Path | str, field_strength : float | int = 500) -> np.ndarray:
    df = DataFrame(str(file))

    if df.array is None:
        raise ValueError("nmrPype array is empty!")
    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")

    x_vals = np.arange(1, len(df.array) + 1)

    init_sw: float = df.getParam("NDSW")
    init_obs: float = df.getParam("NDOBS")
    init_orig: float = df.getParam("NDORIG")
    init_size: float = df.getParam("NDSIZE")

    init_sw = 1.0 if (init_sw == 0.0) else init_sw
    init_obs = 1.0 if (init_obs == 0.0) else init_obs

    delta: float = -init_sw / (init_size)
    first: float = init_orig - delta * (init_size - 1)

    specValPPM = (first + (x_vals - 1.0) * delta) / init_obs

    specValHz: list[float] = [ppm * field_strength for ppm in specValPPM]
    return np.vstack((specValHz, df.array))

# ---------------------------------------------------------------------------- #
#                             Default File Loading                             #
# ---------------------------------------------------------------------------- #

def _load_array(path: Path) -> np.ndarray:
    """
    Convert a file on disk to a 2-D np.ndarray with shape (2, N).
        row 0 → x values
        row 1 → y values

    Currently supports:
        .npy   → load directly (must already be shape (2, N))
        .txt / .csv → two-column whitespace/comma-separated text
        other  → attempts np.load, then np.loadtxt
    """
    suffix = path.suffix.lower()
    if suffix == ".npy":
        arr = np.load(str(path))
        if arr.ndim == 1:
            x = np.arange(len(arr), dtype=float)
            return np.vstack([x, arr])
        return arr  # expected shape (2, N)
    elif suffix in (".txt", ".csv"):
        delimiter = "," if suffix == ".csv" else None
        arr = np.loadtxt(str(path), delimiter=delimiter)
        if arr.ndim == 1:
            x = np.arange(len(arr), dtype=float)
            return np.vstack([x, arr])
        if arr.shape[0] == 2:
            return arr
        # assume columns are (x, y)
        return arr.T[:2]
    else:
        # fallback
        try:
            return np.load(str(path))
        except Exception:
            return np.loadtxt(str(path)).T[:2]

# ---------------------------------------------------------------------------- #
#                               Spin File Loading                              #
# ---------------------------------------------------------------------------- #

def _load_spin_matrix(path: Path):
    spin_names, nuclei_frequencies, couplings = _get_spin_matrix(str(path))
    return Spin(spin_names, nuclei_frequencies, couplings)