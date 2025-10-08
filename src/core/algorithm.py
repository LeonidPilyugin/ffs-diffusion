from abc import ABC, abstractmethod
from typing import List, Optional
from .state import State

# class Algorithm(ABC):
#     @abstractmethod
#     def next(
#         self,
#         state: State,
#     ) -> Optional[bool]:
#         pass
#
#     @abstractmethod
#     def next_steps(
#         self,
#         state: State
#     ) -> int:
#         pass
#
#
# class SpAlgorithm(Algorithm):
class SpAlgorithm:
    class Parameter(ABC):
        @abstractmethod
        def estimate(self, state: State) -> float:
            pass

    def __init__(
        self,
        parameter: Parameter,
        top: float,
        bot: float,
        steps: int,
    ):
        self.parameter = parameter
        self.steps = steps
        self.top = top
        self.bot = bot

    def next(self, state: State) -> Optional[bool]:
        now = self.parameter.estimate(state)
        if now < self.bot:
            return False
        elif now > self.top:
            return True
        return None

    def next_steps(
        self,
        state: State
    ) -> int:
        return self.steps

