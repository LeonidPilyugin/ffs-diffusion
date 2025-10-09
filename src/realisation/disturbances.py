import numpy as np
from ..core.disturbance import Disturbance
from ..core.state import State

class VelocityDisturbance(Disturbance):
    def __init__(
        self,
        seed: int,
    ):
        self.random = np.random.default_rng(seed)
        self.d = 0.1

    def disturb(self, state: State) -> State:
        return State(
            positions = state.positions,
            velocities = state.velocities * (1.0 - self.d / 2 + self.random.random(
                state.velocities.shape,
            ) * self.d),
            types = state.types,
            masses = state.masses,
            cell = state.cell,
            origin = state.origin,
            mean_positions = state.mean_positions,
        )
