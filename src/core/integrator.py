from abc import ABC, abstractmethod
from .state import State

class Integrator(ABC):
    @abstractmethod
    def nsteps(
        self,
        n: int,
        mean_last: int,
    ) -> State:
        pass

    @abstractmethod
    def set_state(self, state: State):
        pass
