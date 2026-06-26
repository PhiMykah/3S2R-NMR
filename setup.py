from setuptools import setup, find_packages

setup(
    name="solventspinsim",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "nmrPype",
        "dearpygui",
    ],
    entry_points={
        "console_scripts": [
            "solventspinsim = solventspinsim.main:entry",
            "3S2R = solventspinsim.main:entry",
        ]
    },
    author="Micah Smith",
    author_email="mykahsmith21@gmail.com",
    description='SolventSpinSim aka 3S2R NMR. Technically the 3rd Revision but 3S2R sounds better',
)
