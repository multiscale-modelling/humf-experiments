import numpy as np
import torch
from humf.layers.energy.interacting_sites import InteractingSites
from humf.layers.interaction_sites.atom_centered_static import AtomCenteredStatic
from humf.layers.pair_energy.inverse_distance_polynomial import (
    InverseDistancePolynomial,
)


def create_polynomial_water():
    num_atoms_per_mol = 3
    orders = 12

    initial_params = np.zeros((num_atoms_per_mol, orders))
    sites = AtomCenteredStatic(
        num_atoms_per_mol=3,
        num_params_per_atom=orders,
        initial_params=torch.tensor(initial_params),
    )

    pair_energy = InverseDistancePolynomial(orders)

    return InteractingSites(sites, pair_energy)
