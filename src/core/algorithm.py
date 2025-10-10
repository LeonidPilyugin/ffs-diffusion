from abc import ABC, abstractmethod
from typing import List, Optional
from .state import State
import logging

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
        self.logger = logging.getLogger(__name__)
        self.parameter = parameter
        self.steps = steps
        self.top = top
        self.bot = bot

    def next(self, state: State) -> Optional[bool]:
        now = self.parameter.estimate(state)
        logging.info(f"estimated/top/bot: {now}/{self.top}/{self.bot}")
        if now < self.bot:
            return False
        elif now > self.top:
            return True
        return None

    def next_steps(
        self,
        state: State
    ) -> int:
        return self.steps["run"], self.steps["mean"]

