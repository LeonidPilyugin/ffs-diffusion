from ..core.integrator import Integrator
from ..core.state import State
import openmm
import scipy
import numpy as np
import logging

class OpenmmIntegrator(Integrator):
    def __init__(
        self,
        openmm_type,
        openmm_arguments,
        potentials,
        platform,
        index,
    ):
        self.index = index
        self.integrator = getattr(openmm, openmm_type)(*openmm_arguments)
        self.platform = platform
        self._context = None

        self.length_unit = openmm.unit.angstrom
        self.time_unit = openmm.unit.picosecond
        self.velocity_unit = self.length_unit / self.time_unit
        self.energy_unit = openmm.unit.kilojoule_per_mole
        self.mass_unit = openmm.unit.atom_mass_units
        self.force_unit = self.energy_unit / self.length_unit

        self.potentials = []
        self.potential_data = []

        for p in potentials:
            with open(p["path"]) as f:
                self.potentials.append(
                    openmm.XmlSerializer.deserialize(f.read())
                )
                self.potential_data.append(p.get("particles", None))

    @property
    def context(self):
        if self._context is not None:
            return self._context

        system = openmm.System()
        system.setDefaultPeriodicBoxVectors(
            self.cell[0] / 10, self.cell[1] / 10, self.cell[2] / 10
        )
        for mass in self.masses:
            system.addParticle(mass)

        for force, data in zip(
            self.potentials, self.potential_data
        ):
            if hasattr(force, "addParticle"):
                for i in range(self.masses.shape[0]):
                    force.addParticle(*data[str(self.types[i])])
            system.addForce(force)

        p = openmm.Platform.getPlatformByName(self.platform["name"])

        platform = self.platform
        del platform["name"]
        self._context = openmm.Context(system, self.integrator, p, platform)
        return self._context

    def set_state(self, state: State):
        self._state = state
        self.masses = state.masses
        self.types = state.types
        self.shape = state.positions.shape
        self.cell = state.cell
        self.origin = state.origin

        i = self.index
        logging.info(f"{i}: Setting positions")
        self.context.setPositions(state.positions / 10)
        logging.info(f"{i}: Setting velocities")
        self.context.setVelocities(state.velocities / 10)

    def nsteps(
        self,
        n: int,
        mean_last: int,
    ) -> State:
        assert n >= mean_last

        self.context.getIntegrator().step(n - mean_last)

        positions = np.zeros(self.shape)
        velocities = np.zeros(self.shape)
        u = t = T = 0
        state = self.context.getState({
            "getPositions": True,
            "getVelocities": True,
        })
        last_pos = state.getPositions(asNumpy=True)

        for _ in range(mean_last):
            self.context.getIntegrator().step(1)
            state = self.context.getState(
                getPositions=True,
                getVelocities=True,
                enforcePeriodicBox=False,
                getForces=True,
                getEnergy=True,
            )
            p = state.getPositions(asNumpy=True)
            v = state.getVelocities(asNumpy=True)
            positions = np.add(positions, p.value_in_unit(self.length_unit))
            u += state.getPotentialEnergy().value_in_unit(self.energy_unit)
            t += state.getKineticEnergy().value_in_unit(self.energy_unit)
            T += (self.masses * np.sum(v.value_in_unit(openmm.unit.meter / openmm.unit.second) ** 2, axis=1)).sum()
            last_pos = p

        velocities = state.getVelocities(asNumpy=True).value_in_unit(self.velocity_unit)
        positions /= mean_last
        u /= mean_last
        t /= mean_last
        T /= mean_last
        T /= 1e3 * scipy.constants.N_A
        T /= scipy.constants.k * np.count_nonzero(self.masses) * 3

        TT = t * 2 / 3 / np.count_nonzero(self.masses) / scipy.constants.k * 1e3 / scipy.constants.N_A

        logging.info(f"i: {self.index} T = {T} / {TT}")

        return State(
            positions=last_pos.value_in_unit(self.length_unit),
            mean_positions=positions,
            velocities=velocities,
            types=self.types,
            masses=self.masses,
            cell=self.cell,
            origin=self.origin,
        )
