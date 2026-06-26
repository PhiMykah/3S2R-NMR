import numpy as np

from .types import PeakArray, PeakList


def simulate_peaklist(
    peaklist: PeakList,
    points: int = 800,
    half_height_width: list[float | int] | float | int = 1,
    freq_limits: tuple[float, float] | None = None,
) -> PeakArray:
    """
    Simulate the NMR spectrum represented by the peaklist

    Parameters
    ----------
    peaklist : list[tuple[float,float, int]]
        A list of peaks representing the simulated NMR spectrum for the given spin system
    points : int, optional
        Number of points in the entire spectrum, by default 800
    half_height_width : float | int, optional
        Linewidth at half height (in Hz) for each lorentzian
    freq_limits : tuple[float,float] | None, optional
        Frequency bounds for the simulation, by default None

    Returns
    -------
    2D PeakArray : np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
        2D numpy array of shape (2, points) simulated NMR data

    Notes
    -----
        Adapted from nmrsim's mplplot function in plt.py
    """
    peaklist.sort()
    if freq_limits:
        if (
            isinstance(freq_limits, tuple)
            and len(freq_limits) == 2
            and all(isinstance(x, (int, float)) for x in freq_limits)
        ):
            l_limit, r_limit = min(freq_limits), max(freq_limits)
        else:
            raise ValueError(
                "freq_limits must be a tuple of two numbers (int or float)"
            )
    else:
        l_limit = peaklist[0][0] - 50
        r_limit = peaklist[-1][0] + 50

    # Define frequency axis
    x: PeakArray = np.linspace(l_limit, r_limit, int(points)) # type: ignore
    # Generate intensity axis from peaklist
    y: PeakArray = simulate_lorentzians(x, peaklist, half_height_width)

    return np.vstack((x, y))


def simulate_lorentzians(
    x: PeakArray, peaklist: PeakList, half_height_width: list[float | int] | float | int
) -> np.ndarray:
    """Simulates the y axis of a peak aray using the x axis, peak frequency and intensities, and half_height_width value.

    Parameters
    ----------
    x : np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
        x-axis (frequencies) of the peak (in Hz)
    peaklist : list[tuple[float,float]]
        List of peaks from the NMR spectrum in frequency intensity pairs
    half_height_width : float | int
        Linewidth at half height (in Hz) for each lorentzian

    Returns
    -------
    PeakArray : np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
        Returns the y-axis (intensities) of the peak (in Hz)

    Notes
    -----
        Adapted from nmrsim's math.py
    """
    y: PeakArray = np.zeros_like(x)

    for center, intensity, idx in peaklist:
        if isinstance(half_height_width, (float, int)):
            hhw = half_height_width
        else:
            hhw = half_height_width[idx]
        y += lorentz(x, center, intensity, hhw)
    return y


def lorentz(freq: PeakArray, center: float, intensity: float, hhw: float) -> PeakArray:
    """
    Calculates a lorentzian value with given parameters

    Parameters
    ----------
    freq : np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
        Frequency (in Hz) to evaluate the intensity
    center : float
        Center of the frequency distribution
    intensity : float
        Relative intensity of the signal
    hhw : float
        Half-height width of the signal

    Returns
    -------
    PeakArray : np.ndarray[tuple[Any, ...], np.dtype[np.float64]]
        The intensity of the lorentzian distribution at the given frequency `freq`

    Notes
    -----
        Adapted from nmrsim's math.py
    """
    if hhw == 0.0:
        hhw = 1e-6

    # Scaling factor lowers peak intensities and broadens values
    scaling_factor = 0.5 / hhw
    return (
        scaling_factor
        * intensity
        * ((0.5 * hhw) ** 2 / ((0.5 * hhw) ** 2 + (freq - center) ** 2))
    )
