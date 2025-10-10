import numpy as np
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import struct

@dataclass
class State:
    positions: np.ndarray
    mean_positions: Optional[np.ndarray]
    velocities: np.ndarray
    types: np.ndarray
    masses: np.ndarray
    cell: np.ndarray
    origin: np.ndarray

    def dump(self, path: Path):
        if self.mean_positions is not None:
            np.savez(
                path,
                pos = self.positions,
                mpos = self.mean_positions,
                vel = self.velocities,
                ty = self.types,
                ms = self.masses,
                cell = self.cell,
                origin = self.origin,
            )
        else:
            np.savez(
                path,
                pos = self.positions,
                vel = self.velocities,
                ty = self.types,
                ms = self.masses,
                cell = self.cell,
                origin = self.origin,
            )

        if self.mean_positions is not None:
            self.write_lammps(path.with_suffix(".lammpsdump"))

    def write_lammps(self, path: Path):
        with open(path, "w") as f:
            f.write(f"ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{self.positions.shape[0]}\n")
            f.write(f"ITEM: BOX BOUNDS pp pp pp\n")
            for i in range(3):
                f.write(f"{self.origin[i]} {self.origin[i] + self.cell[i, i]}\n")
            f.write(f"ITEM: ATOMS id type mass x y z\n")
            for i in range(self.positions.shape[0]):
                f.write(f"{i} {self.types[i]} {self.masses[i]} {self.mean_positions[i,0]} {self.mean_positions[i,1]} {self.mean_positions[i,2]}\n")

    # def write_lammps(self, path: Path):
    #     with open(path, "wb") as f:
    #         magic_string = "DUMPCUSTOM"
    #         f.write(struct.pack("q", -len(magic_string)))
    #         f.write(magic_string.encode())
    #         f.write(struct.pack("i", 1))
    #         f.write(struct.pack("i", 2))
    #         f.write(struct.pack("q", 0))
    #         f.write(struct.pack("q", self.positions.shape[0]))
    #
    #         f.write(struct.pack("i", 2))
    #         for i in range(6):
    #             f.write(struct.pack("i", 0))
    #
    #         for i in range(3):
    #             for j in range(3):
    #                 f.write(struct.pack("d", self.cell[i,j]))
    #         for i in range(3):
    #             f.write(struct.pack("d", self.origin[i]))
    #
    #
    #         f.write(struct.pack("i", 5))
    #         f.write(struct.pack("i", 0))
    #         f.write(struct.pack("B", 0))
    #
    #         columns = "id type x y z"
    #         f.write(struct.pack("i", len(columns)))
    #         f.write(columns.encode())
    #
    #         size_one = 5
    #         max_buff_size = 1024 * 32
    #         max_lines = (max_buff_size // (size_one * 8))
    #         max_n = size_one * max_lines
    #         particles_size = self.positions.shape[0]
    #         nchunk = particles_size // max_lines
    #         if nchunk * max_lines != particles_size: nchunk += 1
    #         index = 0
    #
    #         f.write(struct.pack("i", nchunk))
    #
    #         for i in range(nchunk - 1):
    #             f.write(struct.pack("i", max_n))
    #             for j in range(max_lines):
    #                 f.write(struct.pack("d", float(index)))
    #                 f.write(struct.pack("d", float(self.types[index])))
    #                 for k in range(3):
    #                     f.write(struct.pack("d", self.mean_positions[index,k]))
    #                 index += 1
    #
    #         last_size = particles_size - (nchunk - 1) * max_lines
    #         last_n = size_one * last_size
    #         f.write(struct.pack("i", last_n))
    #
    #         for j in range(last_size):
    #             f.write(struct.pack("d", float(index)))
    #             f.write(struct.pack("d", float(self.types[index])))
    #             for k in range(3):
    #                 f.write(struct.pack("d", self.mean_positions[index,k]))
    #             index += 1


    @staticmethod
    def load(path: Path):
        n = np.load(path, allow_pickle=True)
        if "mpos" in n:
            return State(
                positions=n["pos"],
                mean_positions=n["mpos"],
                velocities=n["vel"],
                types=n["ty"],
                masses=n["ms"],
                cell=n["cell"],
                origin=n["origin"],
            )
        else:
            return State(
                positions=n["pos"],
                mean_positions=None,
                velocities=n["vel"],
                types=n["ty"],
                masses=n["ms"],
                cell=n["cell"],
                origin=n["origin"],
            )

