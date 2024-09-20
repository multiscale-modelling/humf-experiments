import numpy as np
from humf.layers.energy.lennard_jones_coulomb import LennardJonesCoulomb
from humf.layers.interaction_sites.atom_centered_static import AtomCenteredStatic


def create_ljc_water():
    initial_lj_params = np.array([[0.1521, 3.1507], [0.01, 1.0]])
    lennard_jones_sites = AtomCenteredStatic(
        initial_type_params=initial_lj_params,
        type_index=[0, 1, 1],  # 0: O, 1: H
    )

    initial_charges = np.array([[-1.0], [0.5]])
    coulomb_sites = AtomCenteredStatic(
        initial_type_params=initial_charges,
        type_index=[0, 1, 1],  # 0: O, 1: H
    )

    return LennardJonesCoulomb(lennard_jones_sites, coulomb_sites)
