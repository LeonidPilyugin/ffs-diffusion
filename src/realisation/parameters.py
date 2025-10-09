import numpy as np
from ..core.algorithm import SpAlgorithm
from ..core.state import State

class Parameter(SpAlgorithm.Parameter):
    def __init__(self, index):
        self.index = index

    def estimate(self, state: State) -> float:
        def wrap_periodic(pos):
            diag = np.diag(state.cell)
            lo = state.origin
            hi = lo + diag
            return np.fmod(
                pos + diag * np.ceil((lo - np.min(pos, axis=0)) / diag + 1),
                diag
            )


        return np.sum(wrap_periodic(state.positions), axis=0)[self.index]
