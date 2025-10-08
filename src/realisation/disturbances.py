import numpy as np
from ..core.disturbance import Disturbance
from ..core.state import State

class VelocityDisturbance(Disturbance):
    def __init__(
        self,
        seed: int,
    ):
        self.random = np.random.default_rnd(seed)
        self.d = 0.1

    def disturb(self, state: State) -> State:
        return State(
            state.positions,
            state.velocities * (1.0 - self.d / 2 + self.random.random(
                state.velocities.shape,
            ) * self.d),
            state.types,
        )
