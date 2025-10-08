from typing import List
from ..core.stopcrit import StopCriterion as AbstractStopCriterion
from ..core.trajectory import Trajectory

class StopCriterion(AbstractStopCriterion):
    def __init__(self, val):
        self.val = val

    def should_continue(self, trajectories: List[Trajectory]) -> bool:
        return sum([int(t.result) for t in trajectories]) < self.val
