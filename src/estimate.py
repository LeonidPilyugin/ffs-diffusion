#!/usr/bin/env python3

from .readlammps import read_lammps
from .main import load_state, load_parameter, load_class
from .realisation import integrators
import tomllib
import sys
from pathlib import Path

# def main():
#     data = None
#     with open(sys.argv[1], "rb") as f:
#         data = tomllib.load(f)
#     state = load_state(data["state"])
#     parameter = load_parameter(data["parameter"])
#
#     print(parameter.estimate(state))

def main2():
    data = None
    with open(sys.argv[1], "rb") as f:
        data = tomllib.load(f)

    print("step,lambda")
    for p in Path(data["path"]).glob("*.mean"):
        state = load_state(
            data["state"] | { "path": str(p) }
        )
        state.mean_positions = state.positions
        parameter = load_parameter(data["parameter"])
        print(f"{p.stem},{parameter.estimate(state)}")


def main():
    data = None
    with open(sys.argv[1], "rb") as f:
        data = tomllib.load(f)
    state = load_state(data["state"])
    state.mean_positions = state.positions
    parameter = load_parameter(data["parameter"])
    print(parameter.estimate(state))
    integr = data["integrator"]
    integrator = load_class(
        integrators,
        integr["type"],
        integr["arguments"] | { "index": 0 },
    )
    integrator.set_state(state)
    state = integrator.nsteps(1000, 1000)
    state.write_lammps("/tmp/state.lammpsdump")

    #
    # for i in range(10):
    #     integrator.set_state(state)
    #     state = integrator.nsteps(**data["steps"])
    #     print(parameter.estimate(state))
