from .state import State
from .integrator import Integrator
from .algorithm import SpAlgorithm
import logging
from pathlib import Path

class Flux:
    def __init__(
        self,
        state: State,
        integrator: Integrator,
        N: int,
        path: Path,
        parameter: SpAlgorithm.Parameter,
        barriers,
    ):
        self.state = state
        self.time = 0
        self.STEPS = 1000
        self.t2fs = self.STEPS
        self.N = N
        self.parameter = parameter
        self.integrator = integrator
        self.right = barriers["right"][0]
        self.left = barriers["left"][0]
        self.path = path
        self.path.mkdir(exist_ok=True, parents=True)
        self.right_states = []
        self.left_states = []

    def compute_flux(self):
        logging.info("Computing flux")
        n_left = n_right = 0
        self.time = 0
        state = self.state
        self.integrator.set_state(state)
        state = self.integrator.nsteps(self.STEPS, self.STEPS)
        par = self.parameter.estimate(state)
        while max(n_left, n_right) < self.N:
            logging.info(f"Performing step {self.t}")
            newstate = self.integrator.nsteps(self.STEPS, self.STEPS)
            newpar = self.parameter.estimate(newstate)

            logging.info(f"nl/nr/par/newpar/ll/lr {n_left}/{n_right}/{par}/{newpar}/{self.left/self.right}")

            if par < self.right < newpar:
                n_right += 1
                state.dump(self.path / f"{n_right}.right.pkl")
                self.right_states.append(state)
            if par > self.left > newpar:
                n_left += 1
                state.dump(self.path / f"{n_left}.left.pkl")
                self.left_states.append(state)

            self.time += 1
            state = newstate
            par = newpar

        if n_right > n_left:
            self.direction = "right"
            self.states = self.right_states
        else:
            self.direction = "left"
            self.states = self.left_states

    @property
    def t(self):
        return self.time * self.t2fs

    @property
    def flux(self):
        return self.N / self.t


