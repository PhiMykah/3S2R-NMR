from enum import Enum
from sys import stderr

import numpy as np
from numpy.typing import ArrayLike

from solventspinsim.spin.peak import gen_peaklist_weak
from solventspinsim.spin.types import PeakList
from solventspinsim.simulate import simulate_peaklist

class CouplingStrength(Enum):
    WEAK = 0
    STRONG = 1


class Spin:
    """
    A class representing a spin system for NMR (Nuclear Magnetic Resonance) simulations.
    Encapsulates the properties of nuclei, their resonance frequencies, scalar couplings,
    spectral linewidths, and the coupling type for simulation.

    Attributes
    ----------
    _nuclei_number : int
        Number of nuclei in the spin system (inferred from the length of nuclei_frequencies)
    nuclei_frequencies : list[float] | list[int]
        List of resonance frequencies (in Hz) for each nucleus in the spin system
    couplings : ArrayLike (ndarray)
        2D matrix (n x n) of scalar coupling constants or J-couplings between nuclei
    half_height_width : list[float | int] | float | int
        Peak width at half height (in Hz) for spectral lines for each peak group
    coupling_strength : CouplingStrength
        Enum indicating the coupling type for simulation (e.g., weak coupling or strong coupling)

    Raises
    ------
    TypeError
        If input types for nuclei_frequencies, couplings, half_height_width, or coupling_strength are invalid
    ValueError
        If couplings is not a square matrix of shape (n, n) or if coupling_strength is not a valid value

    Methods
    -------
    peaklist() -> list[tuple[float,float]]
        Generates and returns a PeakList object based on the current coupling strength
    """

    def __init__(
        self,
        spin_names: list[str] = [],
        nuclei_frequencies: list[float] | list[int] = [],
        couplings: ArrayLike = np.empty((0, 0)),
        half_height_width: list[float | int] | float | int = 0.5,
        field_strength: float = 500,
        intensities: list[float | int] | None = None,
        coupling_strength: CouplingStrength | str | int = CouplingStrength.WEAK,
    ) -> None:
        """
        Initializes a Spin object with specified nuclear frequencies, coupling matrix, linewidth, and coupling strength.

        Parameters
        ----------
            spin_names : list of str
                Names of the atoms for each nuclei frequency
            nuclei_frequencies : list of float
                List of resonance frequencies (in ppm to be converted to Hz) for each nucleus in the spin system
            couplings : ArrayLike
                2D matrix (n x n) of scalar coupling constants (in Hz) between nuclei. Each row corresponds to a nucleus,

                and each element in the row is the coupling to another nucleus
            half_height_width : float or int, optional
                Linewidth at half height (in Hz) for each resonance, by default 0.5
            coupling_strength : CouplingStrength | str | int, optional
                Enum specifying the coupling regime (e.g., WEAK or STRONG), by default CouplingStrength.WEAK

                Alternatively, input 0 for weak and 1 for strong or "weak"/"strong" strings

        Returns
        -------
        None
        """
        self._nuclei_number: int = len(nuclei_frequencies)
        self.spin_names = spin_names
        self.field_strength = field_strength
        self.nuclei_frequencies = nuclei_frequencies
        self.couplings = couplings
        self.half_height_width = half_height_width
        self.coupling_strength = coupling_strength
        self.intensities = intensities
        self.nuclei_peak_indices = []

    # ---------------------------------------------------------------------------- #
    #                              Getters and Setters                             #
    # ---------------------------------------------------------------------------- #

    @property
    def spin_names(self) -> list[str]:
        return self._spin_names

    @spin_names.setter
    def spin_names(self, value: list[float] | list[int] | list[str]):
        if not isinstance(value, list) or not all(
            isinstance(x, (str, float, int)) for x in value
        ):
            raise TypeError("spin_names must be a list of floats or ints")
        self._spin_names: list[str] = [str(name) for name in value]

    # ------------------------------ field_strength ------------------------------ #

    @property
    def field_strength(self) -> float:
        return self._field_strength

    @field_strength.setter
    def field_strength(self, value: float) -> None:
        try:
            self._field_strength: float = abs(float(value))
        except Exception:
            raise TypeError("field_strength must be a numeric value.")

    # ---------------------------- nuclei_frequencies ---------------------------- #

    @property
    def nuclei_frequencies(self) -> list[float] | list[int]:
        return self._nuclei_frequencies

    @nuclei_frequencies.setter
    def nuclei_frequencies(self, value: list[float] | list[int]) -> None:
        if not isinstance(value, list) or not all(
            isinstance(x, (float, int)) for x in value
        ):
            raise TypeError("nuclei_frequencies must be a list of floats or ints")
        self._ppm_nuclei_frequencies: list[float] | list[int] = value
        self._nuclei_frequencies: list[float] | list[int] = _ppm_to_hz(
            value, self._field_strength
        )

    # --------------------------------- couplings -------------------------------- #

    @property
    def couplings(self) -> ArrayLike:
        return self._couplings

    @couplings.setter
    def couplings(self, value: ArrayLike) -> None:
        n = self._nuclei_number
        if isinstance(value, list) and len(value) == 0:
            arr = np.empty((n, n))
        elif isinstance(value, list) and len(value) == (n * n):
            arr = np.array(value).reshape(n, n)
        else:
            arr = np.array(value)

        if arr.ndim != 2 or arr.shape[0] != n or arr.shape[1] != n:
            raise ValueError(
                f"couplings must be a 2D square matrix of shape ({n}, {n})"
            )
        if not np.issubdtype(arr.dtype, np.number):
            raise TypeError("couplings matrix must contain numeric values")
        self._couplings: np.ndarray = arr

    # ----------------------------- half_height_width ---------------------------- #

    @property
    def half_height_width(self) -> list[float | int]:
        return self._half_height_width

    @half_height_width.setter
    def half_height_width(self, value: list[float | int] | float | int) -> None:
        if isinstance(value, (float, int)):
            self._half_height_width: list[float | int] = [value] * self._nuclei_number
        elif isinstance(value, list) and all(
            isinstance(x, (float, int)) for x in value
        ):
            if len(value) != self._nuclei_number:
                raise ValueError(
                    f"half_height_width list must have length {self._nuclei_number}"
                )
            self._half_height_width: list[float | int] = value
        else:
            raise TypeError(
                "half_height_width must be a float, int, or list of floats/ints"
            )

    # ----------------------------- coupling_strength ---------------------------- #

    @property
    def coupling_strength(self) -> CouplingStrength:
        return self._coupling_strength

    @coupling_strength.setter
    def coupling_strength(self, value: CouplingStrength | str | int) -> None:
        if isinstance(value, CouplingStrength):
            self._coupling_strength: CouplingStrength = value
        elif isinstance(value, str):
            if value.lower() == "weak":
                self._coupling_strength = CouplingStrength.WEAK
            elif value.lower() == "strong":
                self._coupling_strength = CouplingStrength.STRONG
            else:
                raise ValueError("Invalid coupling strength string")
        elif isinstance(value, int):
            if value == 0:
                self._coupling_strength = CouplingStrength.WEAK
            elif value == 1:
                self._coupling_strength = CouplingStrength.STRONG
            else:
                raise ValueError("Invalid coupling strength integer")
        else:
            raise TypeError("Invalid type for coupling_strength")

    # -------------------------------- intensities ------------------------------- #

    @property
    def intensities(self) -> list[float | int]:
        return self._intensities

    @intensities.setter
    def intensities(self, value: list[float | int] | None) -> None:
        if value is None:
            self._intensities: list[float | int] = [1.0] * self._nuclei_number
        elif isinstance(value, list) and all(
            isinstance(v, (float, int)) for v in value
        ):
            self._intensities: list[float | int] = value
        else:
            try:
                new_value = [float(v) for v in value]
                self._intensities: list[float | int] = new_value
            except Exception:
                raise TypeError("Invalid type for intensities")

    # ---------------------------------------------------------------------------- #
    #                                   Functions                                  #
    # ---------------------------------------------------------------------------- #

    def peaklist(self, intensities: list[float | int] | None = None) -> PeakList:
        """
        Generates and returns a PeakList object based on the current coupling strength.
        Depending on whether the coupling strength is strong or not, this method calls the appropriate
        peak list generation function:

            - `gen_peaklist_strong`: See documentation at `spin.peak.gen_peaklist_strong`
            - `gen_peaklist_weak`: See documentation at `spin.peak.gen_peaklist_weak`

        Both functions use the nuclei frequencies and couplings associated with the Spin object.

        Returns
        -------
        PeakList : list[tuple[float, float, int]]
            The generated peak list for the current spin system
        """
        if intensities is not None:
            self.intensities = intensities
        match self._coupling_strength:
            case CouplingStrength.STRONG:
                # return gen_peaklist_strong(self._nuclei_frequencies, self._couplings)
                print(
                    "Strong coupling peak list generation is still in development. Defaulting to weak coupling.",
                    file=stderr,
                )
                return gen_peaklist_weak(
                    self._nuclei_frequencies, self._couplings, self.intensities
                )
            case _:
                return gen_peaklist_weak(
                    self._nuclei_frequencies, self._couplings, self.intensities
                )




def _get_spin_matrix(
    file: str,
) -> tuple[list[str], list[float] | list[int], np.ndarray]:
    """
    Parse a text file for a spin matrix, collecting the coupling matrix and nuclei frequencies

    Parameters
    ----------
    file : str
        File path for the text file

    Returns
    -------
    nuclei_frequencies : list[float] | list[int]
        List of resonance frequencies (in Hz) for each nucleus in the spin system
    couplings : np.ndarray
        2D matrix (n x n) of scalar coupling constants or J-couplings between nuclei
    """

    with open(file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Last line is spin names
    spin_names = lines[0].split()  # skip the first column header

    # All lines except last are matrix rows
    matrix_lines = lines[1:-1]  # skip the first header and last spin names

    N = len(spin_names)
    cmat = np.zeros((N, N), dtype=float)
    chem_shifts = []

    for i, line in enumerate(matrix_lines):
        parts = line.split()
        # Diagonal value is the chemical shift
        chem_shifts.append(float(parts[i + 1]))
        for j in range(N):
            if i == j:
                cmat[i, j] = 0.0  # Set diagonal (chemical shift) to 0
            else:
                cmat[i, j] = float(parts[j + 1])
    # Reflect cmat across the diagonal to ensure symmetry
    cmat = cmat + cmat.T

    return spin_names, chem_shifts, cmat


def _ppm_to_hz(ppm: list[float] | list[int], spec_freq: float):
    """Given a chemical shift in ppm and spectrometer frequency in MHz, return the corresponding chemical shift in Hz."""
    return [d * spec_freq for d in ppm]

def _simulate_spin(spin : Spin, points: int, hhw: list[float | int] | float | int) -> None | np.ndarray:
    if not spin._spin_names:
        return

    simulation = simulate_peaklist(spin.peaklist(), points, hhw)

    return np.array([simulation[0], simulation[1]])