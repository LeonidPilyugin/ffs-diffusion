from typing import List
from ..core.stopcrit import StopCriterion as AbstractStopCriterion
from ..core.trajectory import Trajectory

class StopCriterion(AbstractStopCriterion):
    def __init__(self, val):
        self.val = val

    def should_continue(self, trajectories: List[Trajectory]) -> bool:
        sm = sum([1 if t.result else 0 for t in trajectories])
        return  sm < self.val
