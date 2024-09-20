import numpy as np
from humf.layers.energy.interacting_sites import InteractingSites
from humf.layers.interaction_sites.atom_centered_static import AtomCenteredStatic
from humf.layers.pair_energy.inverse_distance_polynomial import (
    InverseDistancePolynomial,
)


def create_polynomial_water():
    num_types = 2
    orders = 12

    initial_type_params = np.zeros((num_types, orders))
    sites = AtomCenteredStatic(
        initial_type_params=initial_type_params,
        type_index=[0, 1, 1],  # 0: O, 1: H
    )

    pair_energy = InverseDistancePolynomial(orders)

    return InteractingSites(sites, pair_energy)
