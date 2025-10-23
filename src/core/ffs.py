from typing import List
from dataclasses import dataclass
from pathlib import Path
import json
import logging
from .algorithm import SpAlgorithm
from .integrator import Integrator
from .trajectory import Trajectory
from .executor import Executor
from .stopcrit import StopCriterion
from .disturbance import Disturbance
from .state import State
from .flux import Flux

class Ffs:
    def __init__(
        self,
        path: Path,
        executor: Executor,
        parameter: SpAlgorithm.Parameter,
        states: List[State],
        stopcrit: StopCriterion,
        barriers: List[float],
        disturbance: Disturbance,
        steps: int,
        integrator: Integrator,
        flux: dict,
    ):
        self.logger = logging.getLogger(__name__)
        self.path = path
        self.states = states
        self.trajectories = []
        self.barriers = barriers
        self.stopcrit = stopcrit
        self.disturbance = disturbance
        self.executor = executor
        self.steps = steps
        self.parameter = parameter

        self.flux = Flux(
            self.states[0],
            integrator,
            flux["N"],
            path / "flux",
            parameter,
            barriers,
        )

        if self.path.joinpath("data.json").exists():
            self.load_checkpoint()

        self.logger.info("Ffs object loaded")

    def load_checkpoint(self):
        self.logger.info("Loading checkpoint")
        with open(self.path / "data.json", "r") as f:
            d = json.load(f)
            self.probabilities = d["probabilities"]
            self.total = d["total"]
            self.success = d["success"]
            self.barriers = d["barriers"]
            self.steps = d["steps"]

        ppath = self.path / f"ph{self.phase}"
        self.states = []
        for filename in ppath.glob("*.pkl"):
            self.states.append(State.load(ppath / filename))

    def dump_checkpoint(self):
        self.logger.info("Dumping checkpoint")
        with open(self.path / "data.json", "w") as f:
            json.dump(
                {
                    "probabilities": self.probabilities,
                    "total": self.total,
                    "success": self.success,
                    "barriers": self.barriers,
                    "steps": self.steps,
                    "flux": {
                        "flux": self.flux.flux,
                        "t": self.flux.t,
                        "N": self.flux.N,
                    },
                }, f, indent=2
            )

        ppath = self.path / f"ph{self.phase}"
        ppath.mkdir(parents=True, exist_ok=True)
        for i, s in enumerate(self.states):
            s.dump(ppath / f"st{i}.pkl")

    @property
    def phase(self) -> int:
        return len(self.probabilities) - self.probabilities.count(None)

    @property
    def finished(self) -> bool:
        return self.phase == len(self.probabilities)

    def next_phase(self):
        self.logger.info(f"Starting phase {self.phase}")
        def next_state():
            if next_state.counter >= len(self.states):
                self.states.append(
                    self.disturbance.disturb(
                        self.states[next_state.dcounter]
                    )
                )
                next_state.dcounter += 1

            next_state.counter += 1
            return self.states[next_state.counter - 1]

        next_state.counter = 0
        next_state.dcounter = 0

        self.trajectories.clear()

        while self.stopcrit.should_continue(self.trajectories):
            self.logger.info("Stop criterion not reached")
            newtrajs = []

            for _ in range(self.executor.max_parallel):
                self.logger.info("Appending trajectory")
                newtrajs.append(Trajectory(
                    next_state(),
                    SpAlgorithm(
                        self.parameter,
                        self.barriers[self.phase + 1],
                        # self.barriers[self.phase - 1],
                        self.barriers[0],
                        self.steps,
                    ),
                ))

            self.executor.submit(newtrajs)
            self.trajectories.extend(newtrajs)
            self.logger.info("Next stage")

        self.total[self.phase] = len(self.trajectories)
        self.success[self.phase] = sum(
            [1 if t.result else 0 for t in self.trajectories]
        )
        self.probabilities[self.phase] = \
            self.success[self.phase] / self.total[self.phase]

    def start(self):
        self.flux.compute_flux()
        self.states = self.flux.states
        self.barriers = self.barriers[self.flux.direction]
        self.probabilities = [None] * (len(self.barriers) - 1)
        self.total = [None] * (len(self.barriers) - 1)
        self.success = [None] * (len(self.barriers) - 1)
        self.logger.info("Starting calculations")
        while not self.finished:
            self.next_phase()
            self.states = [
                t.state for t in self.trajectories if t.result
            ]
            self.dump_checkpoint()
        self.logger.info("Calculations finished")

