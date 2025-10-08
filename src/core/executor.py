from abc import ABC, abstractmethod
from typing import List
from .trajectory import Trajectory

class Executor(ABC):
    @abstractmethod
    def submit(self, trajectories: List[Trajectory]):
        pass

    @property
    @abstractmethod
    def max_parallel(self) -> int:
        pass
