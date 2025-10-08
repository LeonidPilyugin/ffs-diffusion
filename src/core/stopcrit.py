from abc import ABC, abstractmethod
from typing import List
from .trajectory import Trajectory

class StopCriterion(ABC):
    @abstractmethod
    def should_continue(self, trajectories: List[Trajectory]) -> bool:
        pass
