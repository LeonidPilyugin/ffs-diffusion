#!/usr/bin/env python3

import sys
import json
from .core.ffs import Ffs
from .realisation import executors, parameters, stopcriteria, disturbances, integrators
from .readlammps import read_lammps
from pathlib import Path
import random
import logging

def load_steps(data):
    return data

def load_state(data):
    state =  read_lammps(data["path"])

    radius = data["radius"]
    random.seed(data["seed"])
    trsh = data["trsh"]

    lx = state.cell[0,0]
    ly = state.cell[1,1]
    lz = state.cell[2,2]
    ox, oy, oz = state.origin

    for i in range(len(state.masses)):
        x, y, z = state.positions[i,:]

        if all([
            abs(x - ox - lx / 2) > radius,
            abs(y - oy - ly / 2) > radius,
            abs(z - oz - lz / 2) > radius,
            random.random() < trsh
        ]):
            state.masses[i] = 0.0



    return state

def load_barriers(data):
    return data["barriers"]

def load_class(module, name, args):
    return getattr(module, name)(**args)

def load_parameter(data):
    return load_class(parameters, data["type"], data["arguments"])

def load_executor(data):
    integrs = []
    gl = data["integrator"]["global"]
    for i in data["integrator"]["individual"]:
        integrs.append(load_class(integrators, gl["type"],
            gl["arguments"] | i,
        ))
    return load_class(
        executors,
        data["type"],
        data["arguments"] | { "integrators": integrs }
    )

def load_stopcriterion(data):
    return load_class(stopcriteria, data["type"], data["arguments"])

def load_disturbance(data):
    return load_class(disturbances, data["type"], data["arguments"])

def main():
    root = Path(sys.argv[1])

    logging.basicConfig(
        filename = root / "log",
        level=logging.INFO,
    )

    data = None
    with open(root / "descriptor.json", "r") as f:
        data = json.load(f)

    Ffs(
        path=root,
        executor=load_executor(data["ffs"]["executor"]),
        parameter=load_parameter(data["ffs"]["parameter"]),
        states=[load_state(data["ffs"]["state"])],
        stopcrit=load_stopcriterion(data["ffs"]["stopcriterion"]),
        barriers=load_barriers(data["ffs"]["barriers"]),
        disturbance=load_disturbance(data["ffs"]["disturbance"]),
        steps=load_steps(data["ffs"]["steps"]),
    ).start()

if __name__ == "__main__":
    main()
