from .realisation.parameters import BubbleCenterParameter, WSBCParameter
from .readlammps import read_lammps
from .core.state import State
import sys
import numpy as np
from pathlib import Path

def main():
    path = sys.argv[1]
    index = 0
    treshold = 4.2
    gridstep = 0.5
    trsh = 5.0

    state = None

    try:
        state = read_lammps(path)
    except:
        state = State.load(path)
    state.mean_positions = state.positions
    p = WSBCParameter(
        index,
        sys.argv[2],
        trsh,
        {
            "eps": 5.0
        }
    )

    p.estimate(state)

    p.reference.mean_positions = p.reference.positions


    p.reference.write_lammps(Path(sys.argv[3]))
