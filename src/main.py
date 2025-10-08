#!/usr/bin/env python3

import sys
import json
from .core.ffs import Ffs
import .realisation.parameters as parameters
import .realisation.executors as executors
import .realisation.stopcriteria as stopcriteria
import .realisation.disturbances as disturbances
import .realisation.integrators as integrators
from .readlammps import read_lammps
from pathlib import path

def load_steps(data):
    return data

def load_state(data):
    return read_lammps(data["path"])

def load_barriers(data):
    return data["barriers"]

def load_class(module, name, args):
    return getattr(module, name)(**args)

def load_parameter(data):
    return load_class(parameters, data["type"], data["arguments"])

def load_executor(data):
    integrators = []
    gl = data["global"]
    for i in data["integrator"]["individual"]:
        integrators.append(load_class(integrators, gl["type"],
            gl["arguments"] | i,
        ))
    return load_class(
        executors,
        data["type"],
        data["arguments"] | { "integrators": integrators }
    )

def load_stopcriterion(data):
    return load_class(stopcriteria, data["type"], data["arguments"])

def load_disturbance(data):
    return load_class(disturbances, data["type"], data["arguments"])

def main():
    root = Path(sys.argv[1])

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
        steps=load_steps(data["ffs"]["disturbance"]),
    ).start()

if __name__ == "__main__":
    main()
