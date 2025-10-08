from abc import ABC, abstractmethod
from .state import State

class Integrator(ABC):
    @abstractmethod
    def nsteps(
        self,
        n: int = 1,
        mean_last: int = 1000,
    ) -> State:
        pass

    @abstractmethod
    def set_state(self, state: State):
        pass
