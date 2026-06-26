from collections import Counter
from typing import Literal

import numpy as np

from solventspinsim.spin.types import Peak, PeakList

# ---------------------------------------------------------------------------- #
#                              Generate Couplings                              #
# ---------------------------------------------------------------------------- #


def gen_peaklist_weak(
    nuclei_frequencies: list[float] | list[int],
    J_couplings: np.ndarray,
    intensities: list[float | int],
) -> PeakList:
    """
    Generate a peak list for a weakly coupled spin system.
    This function simulates the NMR peak list for a set of nuclei with given resonance frequencies and J-coupling constants,
    assuming weak coupling (first-order approximation). For each nucleus, it generates the corresponding multiplet pattern
    based on its couplings and combines all signals into a single peak list.

    Parameters
    ----------
        nuclei_frequencies : list[float] | list[int]
            List of resonance frequencies (in Hz) for each nucleus
        J_couplings : np.ndarray
            2D matrix (n x n) of scalar coupling constants (in Hz) between nuclei. Each row corresponds to a nucleus,

            and each element in the row is the coupling to another nucleus
    Returns
    -------
        PeakList: list[tuple[float,float,int]]
            A list of peaks representing the simulated NMR spectrum for the given spin system

    Notes
    -----
        Adapted from nmrsim's firstorder.py
    """
    n = len(nuclei_frequencies)

    if len(intensities) < n:
        intensities = intensities + [1] * (n - len(intensities))
    if len(intensities) > n:
        intensities = intensities[:n]

    peaklist: PeakList = []
    for i, nuclei in enumerate(nuclei_frequencies):
        couplings = ( # Generator[tuple[ArrayLike, int]]
            (j, 1) for j in J_couplings[i] if j != 0
        )
        signal: PeakList = _multiplet((nuclei, intensities[i], i), couplings)
        peaklist += signal
    return _reduce_peaks(sorted(peaklist))


def gen_peaklist_strong(
    nuclei_frequencies: list[float] | list[int], J_couplings: np.ndarray
) -> PeakList:
    # Adapted from nmrsim's qm.py
    return [(0, 0, 0)]


# ---------------------------------------------------------------------------- #
#                               Helper Functions                               #
# ---------------------------------------------------------------------------- #


def _multiplet(signal: tuple, couplings) -> PeakList:
    """
    Generate a multiplet peak list by iteratively applying couplings to an initial signal.

    Parameters
    ----------
    signal : tuple
        The initial peak signal, typically a tuple representing (position, intensity)
    couplings : Generator[tuple[ArrayLike, int]]
        A generator yielding tuples, each containing coupling constants (as an array-like object)
        and the number of equivalent couplings to apply

    Returns
    -------
    PeakList: list[tuple[float,float,int]]
        A sorted list of peaks after applying all couplings

    Notes
    -----
        Adapted from nmrsim's firstorder.py
    """
    peaklist: PeakList = [signal]
    for coupling in couplings:
        for _ in range(coupling[1]):
            peaklist = _doublet(peaklist, coupling[0])
    return sorted(_reduce_peaks(peaklist))


def _doublet(peaklist, coupling_constant) -> PeakList:
    """
    Splits each peak in the input list into a doublet by applying the specified coupling constant.
    Each peak is split into two: one at (frequency - coupling_constant / 2) and one at (frequency + coupling_constant / 2),
    with each new peak having half the original intensity.

    Parameters
    ----------
    peaklist : list[tuple[float,float,int]]
        List of (frequency, intensity, nuclei_idx) tuples representing the original peaks
    coupling_constant : float
        The coupling constant (Hz) used to split each peak

    Returns
    -------
    PeakList :  list[tuple[float,float,int]]
        A new list of (frequency, intensity, nuclei_idx) tuples representing the doublet peaks

    Notes
    -----
        Adapted from nmrsim's firstorder.py
    """
    new_peaklist: PeakList = []
    # For every peak in the list, split the frequency and half the intensity to form doublets
    for freq, intensity, idx in peaklist:
        new_peaklist.append((freq - coupling_constant / 2, intensity / 2, idx))
        new_peaklist.append((freq + coupling_constant / 2, intensity / 2, idx))
    return new_peaklist


def _reduce_peaks(unsorted_peaklist, tolerance=0) -> PeakList:
    """
    Reduces a list of peaks by combining adjacent peaks within a specified tolerance.
    This function sorts the input peak list and iteratively groups peaks whose positions
    are within `tolerance` of each other. Each group of adjacent peaks is then combined
    into a single peak using the `spin.peak.peak_sum` function.

    Parameters
    ----------
        unsorted_peaklist : list[tuple[float,float,int]]
            The list of peaks to be reduced
        tolerance : float, optional
            The maximum allowed difference between peak positions

            for them to be considered adjacent and combined, Defaults to 0

    Returns
    -------
        PeakList : list[tuple[float,float,int]]
            A new list of peaks where adjacent peaks within the specified tolerance
            have been combined

    Notes
    -----
        Adapted from nmrsim's math.py
    """
    new_peaklist: PeakList = []
    work: PeakList = []  # Peaklist of current peaks to be tested
    # Ensure peak list is sorted before performing reduction
    peaklist: PeakList = sorted(unsorted_peaklist)

    for peak in peaklist:
        if not work:
            work.append(peak)
            continue
        if peak[0] - work[-1][0] <= tolerance:
            work.append(peak)
            continue
        else:
            parent_idx = _mode_smallest(work)
            new_peaklist.append(peak_sum(work, parent_idx))

            work = [peak]
    if work:  # Add the remaining work peaks after loop
        parent_idx = _mode_smallest(work)
        new_peaklist.append(peak_sum(work, parent_idx))

    return new_peaklist


def peak_sum(peaklist: PeakList, parent_idx: int) -> Peak:
    """
    Sums up a peak list by adding intensity and finding the average frequency

    Parameters
    ----------
    peaklist : list[tuple[float,float]]
        list of peaks to sum together

    Returns
    -------
    Peak : tuple
        New peak sum with frequency average and intensity total

    Notes
    -----
        Adapted from nmrsim's math.py
    """
    frequency_total: float | Literal[0] = sum(peak[0] for peak in peaklist)
    intensity_total: float | Literal[0] = sum(peak[1] for peak in peaklist)

    return (frequency_total / len(peaklist), intensity_total, parent_idx)


def _mode_smallest(peak_group: PeakList) -> int:
    """
    Returns the mode of parent_idx values in peak_group,
    breaking ties by choosing the smallest index.
    """
    counts = Counter(p[2] for p in peak_group)
    max_count = max(counts.values())
    candidates = [idx for idx, cnt in counts.items() if cnt == max_count]
    return min(candidates)
