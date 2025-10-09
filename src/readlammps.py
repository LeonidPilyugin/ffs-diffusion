from .core.state import State
import numpy as np

class Reader:
    def __init__(self, path):
        self.path = path
        self.f = None
        self._line = None

    def __enter__(self):
        self.f = open(self.path, "r")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()

    @property
    def line(self):
        return self._line

    def __iter__(self):
        return self

    def __next__(self):
        self._line = self.f.readline()
        if not self._line:
            raise StopIteration
        return self.line

    def readline(self):
        return next(self)

def read_box(f):
    edge = np.zeros((3, 3))
    origin = np.zeros((3,))
    if f.line[:16] == "ITEM: BOX BOUNDS":
        for i in range(3):
            f.readline()
            low, high = list(map(float, f.line.split()))
            edge[i, i] = high - low
            origin[i] = low
    else:
        raise RuntimeError("Not implemented")

    return edge, origin


def read_natoms(f):
    return int(f.readline().strip())

def read_atoms(f, natoms):
    assert "ITEM: ATOMS id type mass x y z vx vy vz" == f.line.strip()

    positions = np.empty((natoms,3))
    velocities = np.empty((natoms,3))
    types = np.empty((natoms,), dtype=np.int64)
    masses = np.empty((natoms,))

    for i in range(natoms):
        f.readline()
        id, t, m, x, y, z, vx, vy, vz = f.line.strip().split()
        types[i] = int(t)
        masses[i] = float(m)
        positions[i,:] = list(map(float, [x, y, z]))
        velocities[i,:] = list(map(float, [vx, vy, vz]))

    return masses, types, positions, velocities

def read_lammps(path) -> State:
    cell = origin = natoms = masses = types = positions = velocities = None
    with Reader(path) as f:
        for line in f:
            if line.strip()[:16] == "ITEM: BOX BOUNDS":
                cell, origin = read_box(f)
            if line.strip() == "ITEM: NUMBER OF ATOMS":
                natoms = read_natoms(f)
            if line.strip()[:11] == "ITEM: ATOMS":
                masses, types, positions, velocities = read_atoms(f, natoms)

    return State(
        positions = positions,
        mean_positions = None,
        velocities = velocities,
        types = types,
        masses = masses,
        cell = cell,
        origin = origin,
    )


