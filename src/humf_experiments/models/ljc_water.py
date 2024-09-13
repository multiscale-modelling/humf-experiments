import numpy as np
import torch
from humf.layers.energy.lennard_jones_coulomb import LennardJonesCoulomb
from humf.layers.interaction_sites.atom_centered_static import AtomCenteredStatic


def create_ljc_water():
    num_atoms_per_mol = 3

    initial_lj_params = np.array([[0.1521, 3.1507], [0.0, 1.0], [0.0, 1.0]])
    lennard_jones_sites = AtomCenteredStatic(
        num_atoms_per_mol=num_atoms_per_mol,
        num_params_per_atom=2,
        initial_params=torch.tensor(initial_lj_params, dtype=torch.float32),
    )

    initial_charges = np.array([[-1.0], [0.5], [0.5]])
    coulomb_sites = AtomCenteredStatic(
        num_atoms_per_mol=num_atoms_per_mol,
        num_params_per_atom=1,
        initial_params=torch.tensor(initial_charges, dtype=torch.float32),
    )

    return LennardJonesCoulomb(lennard_jones_sites, coulomb_sites)
