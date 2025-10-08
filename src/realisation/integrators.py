from ...core.integrator import Integrator
from ...core.state import State
import openmm
import scipy
import numpy as np

class OpenmmIntegrator(Integrator):
    def __init__(
        self,
        openmm_type,
        openmm_arguments,
        potentials,
        platform,
    ):
        self.integrator = getattr(openmm, openmm_type)(*openmm_arguments)
        self.platform = platform
        self.potentials = potentials

        self.length_unit = openmm.unit.angstrom
        self.time_unit = openmm.unit.picosecond
        self.velocity_unit = self.length_unit / self.time_unit
        self.energy_unit = openmm.unit.kilojoule_per_mole
        self.mass_unit = openmm.unit.atom_mass_units
        self.force_unit = self.energy_unit / self.length_unit

    def set_state(self, state: State):
        system = openmm.System()
        system.setDefaultPeriodicBoxVectors(
            state.cell[0], state.cell[1], state.cell[2]
        )
        for mass in state.masses:
            system.addParticle(mass)

        self.masses = state.masses
        self.types = state.types

        for force, data in zip(
            self.potentials, self.potential_data
        ):
            if hasattr(force, "addParticle"):
                for i in range(particles.get_size()):
                    force.addParticle(*data[str(types[i])])
            system.addForce(force)

        p = openmm.Platform.getPlatformByName(self.platform["name"])

        context = openmm.Context(system, self.integrator, p, self.platform)
        context.setPositions(state.positions)
        context.setVelocities(state.velocities)

        self.context = context
        self.shape = state.shape

    def nsteps(
        self,
        n: int,
        mean_last: int = 1000,
    ) -> State:
        assert n >= mean_last

        self.context.getIntegrator().step(n - mean_last)

        positions = np.zeroes_like(self.shape)
        velocities = np.zeroes_like(self.shape)
        u = t = T = 0
        last_pos = self.context.getState({
            "getPositions": True,
        }).getPositions(asNumpy=True)

        for _ in range(mean_last):
            self.context.getIntegrator().step(1)
            state = openmm_object.context.getState(
                getPositions=True,
                getVelocities=True,
                enforcePeriodicBox=False,
                getForces=True,
                getEnergy=True,
            )
            p = state.getPositions(asNumpy=True)
            v = state.getVelocities(asNumpy=True)
            positions = np.add(positions, p.value_in_unit(self.length_unit))
            velocities = np.add(velocities, v.value_in_unit(self.velocity_unit))
            u += state.getPotentialEnergy().value_in_unit(self.energy_unit)
            t += state.getKineticEnergy().value_in_unit(self.energy_unit)
            T += (masses * np.sum(v.value_in_unit(openmm.unit.meter / openmm.unit.second) ** 2, axis=1)).sum() / scipy.constants.k / np.count_nonzero(masses) / 3
            last_pos = p

        positions /= mean_last
        velocities /= mean_last
        u /= mean_last
        t /= mean_last
        T /= mean_last

        return State(
            positions=last_pos,
            mean_positions=positions,
            velocities=velocities,
            types=self.types,
            masses=self.masses,
        )
