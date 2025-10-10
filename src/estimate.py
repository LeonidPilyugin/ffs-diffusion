#!/usr/bin/env python3

from .readlammps import read_lammps
from .main import load_state, load_parameter
import tomllib
import sys

def main():
    data = None
    with open(sys.argv[1], "rb") as f:
        data = tomllib.load(f)
    state = load_state(data["state"])
    parameter = load_parameter(data["parameter"])

    print(parameter.estimate(state))

