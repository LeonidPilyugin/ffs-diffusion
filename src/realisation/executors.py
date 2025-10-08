from ..core.executor import Executor as AbstractExecutor
from ..core.trajectory import Trajectory
from ..core.integrator import Integrator
from typing import List
import threading as th

class Executor(AbstractExecutor):
    def __init__(
        self,
        integrators: List[Integrator],
    ):
        self.mp = len(integrators)
        self.integrators = integrators

    def submit(trjs: List[Trajectory]):
        for t in trjs:
            t.integrator = self.integrators[i]

        ths = [Thread(target=lambda x: x.simulate(), args=(t,)) for t in trjs]
        for th in ths:
            th.start()
        for th in ths():
            th.join()

    @property
    def max_parallel(self) -> int:
        return self.mp
