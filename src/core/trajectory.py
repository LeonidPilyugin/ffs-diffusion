from .algorithm import SpAlgorithm as Algorithm
from .state import State

class Trajectory:
    def __init__(
        self,
        initial: State,
        algorithm: Algorithm,
    ):
        self._state = initial
        self._discard = None
        self._integrator = None
        self.algorithm = algorithm

    @property
    def integrator(self):
        return self._integrator

    @integrator.setter
    def integrator(self, integrator):
        integrator.set_state(self._state)
        self._integrator = integrator

    def simulate(self):
        self.previous_state = self.state
        result = None
        while result is None:
            self._state = self.integrator.nsteps(
                *self.algorithm.next_steps(self.state),
            )
            result = self.algorithm.next(self.state)

        self._result = result

    @property
    def state(self) -> State:
        return self._state

    @property
    def result(self):
        return self._discard
