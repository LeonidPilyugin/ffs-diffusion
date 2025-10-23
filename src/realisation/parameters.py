import numpy as np
from scipy.spatial import KDTree
from ..core.algorithm import SpAlgorithm
from ..core.state import State
from ..readlammps import read_lammps
import logging
import sys
from sklearn.cluster import DBSCAN

class Parameter(SpAlgorithm.Parameter):
    def __init__(self, index):
        self.index = index

    def estimate(self, state: State) -> float:
        def wrap_periodic(pos):
            return pos
            diag = np.diag(state.cell)
            lo = state.origin
            hi = lo + diag
            return np.fmod(
                pos + diag * np.ceil((lo - np.min(pos, axis=0)) / diag + 1),
                diag
            )

        return np.sum(wrap_periodic(state.positions), axis=0)[self.index]


class BubbleCenterParameter(SpAlgorithm.Parameter):
    def __init__(self, index, treshold, gridstep):
        self.index = index
        self.grid = None
        self.treshold = treshold
        self.gridstep = gridstep

    def get_grid(self, state):
        if self.grid is None:
            self.grid = np.stack(
                np.meshgrid(
                    *[np.arange(0.0, state.cell[i,i], self.gridstep) for i in range(3)]
                ), axis=-1).reshape(-1, 3)
        return self.grid

    def get_near_points(self, state: State):
        def wrap_periodic(pos):
            diag = np.diag(state.cell)
            lo = state.origin
            return np.fmod(
                pos + diag * np.ceil((lo - np.min(pos, axis=0)) / diag + 1),
                diag
            )

        grid = self.get_grid(state)
        pos = wrap_periodic(state.mean_positions)

        neighbors = KDTree(pos).query_ball_point(
            grid, r=self.treshold, return_length=True
        )
        near_mask = np.array([n == 0 for n in neighbors])
        return grid[near_mask]

    def estimate(self, state: State) -> float:
        near_points = self.get_near_points(state)
        return (np.sum(near_points, axis=0) / near_points.shape[0])[self.index]

class WSBCParameter(SpAlgorithm.Parameter):
    def __init__(self, index, reference, trsh, dbscan):
        reference = read_lammps(reference)
        self.index = index
        self.addorigin = np.ones((3,)) * 0.2
        reference.positions = self.wrap_periodic(
            reference.positions,
            reference.cell,
            reference.origin,
        )
        reference.mean_positions = reference.positions
        self.reference = reference
        self.trsh = trsh

        self.ca = DBSCAN(**dbscan)

    def wrap_periodic(self, pos, cell, origin):
        pos += self.addorigin.T
        diag = np.diag(cell)
        lo = origin
        return np.fmod(
            pos + diag * np.ceil((lo - np.min(pos, axis=0)) / diag + 1),
            diag
        )

    def performws(self, state):
        pos = self.wrap_periodic(
            state.mean_positions,
            state.cell,
            state.origin,
        )
        rpos = self.reference.positions
        kd = KDTree(rpos)
        neighbors = kd.query_ball_point(pos, self.trsh)
        counts = np.zeros((rpos.shape[0],), dtype=np.int32)

        for point, indeces in zip(pos, neighbors):
            near = rpos[indeces]
            distances = np.sqrt(
                np.sum((near - point) ** 2, axis=1)
            )
            nearest = np.argmin(distances)
            counts[indeces[nearest]] += 1

        return counts

    def estimate(self, state: State) -> float:
        counts = self.performws(state)
        vaccancies = self.reference.positions[0 == counts,:]
        labels = self.ca.fit(vaccancies).labels_
        val, cs = np.unique(labels, return_counts=True)
        clust = vaccancies[labels == val[np.argmax(cs)],:]

        # self.reference.types[0 == counts] = 2
        # k = 0
        # for i in range(len(self.reference.types)):
        #     if self.reference.types[i] == 2:
        #         if labels[k] == val[np.argmax(cs)]:
        #             self.reference.types[i] = 3
        #         k += 1

        com = clust.mean(axis=0)
        com -= self.addorigin
        return com[self.index]

