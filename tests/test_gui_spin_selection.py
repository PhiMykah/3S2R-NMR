from pathlib import Path

import numpy as np

from solventspinsim.parse.settings import Settings
from solventspinsim.spin import Spin
from solventspinsim.ui.gui import GUI


def test_get_active_spin_ids_returns_selected_spin(monkeypatch):
    gui = GUI("Test", Settings())
    first = gui.get_file_manager().add_spin(Path("one.txt"), Spin(
        spin_names=["A"],
        nuclei_frequencies=[0.0],
        couplings=np.empty((1, 1)),
        half_height_width=1.0,
        field_strength=500.0,
        intensities=[1.0],
    ))
    gui.get_file_manager().add_spin(Path("two.txt"), Spin(
        spin_names=["B"],
        nuclei_frequencies=[1.0],
        couplings=np.empty((1, 1)),
        half_height_width=1.0,
        field_strength=500.0,
        intensities=[1.0],
    ))

    monkeypatch.setattr("solventspinsim.ui.gui.dpg.does_item_exist", lambda tag: True)
    monkeypatch.setattr("solventspinsim.ui.gui.dpg.get_value", lambda tag: f"{first.get_label()}|{first.get_id()}")

    assert gui._get_active_spin_ids() == [first.get_id()]


def test_drag_updates_selected_spin_frequency_and_coupling(monkeypatch):
    gui = GUI("Test", Settings())
    spin = Spin(
        spin_names=["A", "B"],
        nuclei_frequencies=[0.0, 1.0],
        couplings=np.array([[0.0, 0.5], [0.5, 0.0]]),
        half_height_width=1.0,
        field_strength=500.0,
        intensities=[1.0, 1.0],
    )
    sf = gui.get_file_manager().add_spin(Path("pair.txt"), spin)
    gui._selected_spin_id = sf.get_id()
    monkeypatch.setattr(gui, "_refresh_main_plot", lambda: None)
    monkeypatch.setattr(gui, "_recenter_main_plot", lambda: None)

    gui._update_selected_spin_frequency(1, 25.0)
    assert spin.nuclei_frequencies[1] == 25.0

    gui._update_selected_spin_coupling(0, 1, 3.0)
    assert spin.couplings[0, 1] == 3.0
    assert spin.couplings[1, 0] == 3.0
