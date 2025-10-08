from abc import ABC, abstractmethod
from .state import State

class Disturbance(ABC):
    @abstractmethod
    def disturb(self, state: State) -> State:
        pass
