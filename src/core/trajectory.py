from .algorithm import SpAlgorithm as Algorithm
from .state import State
import logging

class Trajectory:
    def __init__(
        self,
        initial: State,
        algorithm: Algorithm,
    ):
        self._state = initial
        self._result = None
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
        logging.info("Simulating trajectory")
        self.previous_state = self.state
        result = None
        while result is None:
            run, mean = self.algorithm.next_steps(self.state)
            logging.info(f"Performing {run} steps with {mean} mean")
            self._state = self.integrator.nsteps(run, mean)
            result = self.algorithm.next(self.state)

        logging.info(f"Got {result} result")

        self._result = result

    @property
    def state(self) -> State:
        return self._state

    @property
    def result(self):
        return self._result
