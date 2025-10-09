import numpy as np
from ..core.algorithm import SpAlgorithm
from ..core.state import State

class Parameter(SpAlgorithm.Parameter):
    def __init__(self, index):
        self.index = index

    def estimate(self, state: State) -> float:
        return np.sum(state.positions, axis=0)[self.index]
