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
