# pyright: reportAssignmentType=false

import zntrack as zn

from humf_experiments.data.gromacs.read_2_column_xvg import read_xvg_2_column
from humf_experiments.data.gromacs.read_forces_from_gmx_dump import (
    return_forces_from_gmx_dump_of_trj,
)
from humf_experiments.data.gromacs.simplified_gro_reader import (
    extract_all_coordinates_from_gro_file,
)
from humf_experiments.nodes.zntrack_utils import zop


class CreateGromacsDataset(zn.Node):
    n_h2o_trajectory: str = zn.deps()
    n_h2o_potential_energy: str = zn.deps()
    n_h2o_trajectory_forces: str = zn.deps()

    data_dir: str = zop("data/")

    def run(self):
        times, energies = read_xvg_2_column(self.n_h2o_potential_energy)
        forces_df = return_forces_from_gmx_dump_of_trj(
            self.n_h2o_trajectory_forces, splitstring=None
        )
        trajectory = extract_all_coordinates_from_gro_file(
            self.n_h2o_trajectory, itpfile=None
        )
        assert len(times) == len(energies) == len(forces_df) == len(trajectory)

        for atoms, energy, forces_df in zip(
            trajectory, energies, forces_df["atoms_forces_df"]
        ):
            print("###")
            print(atoms.positions)
            print(energy)
            print(forces_df)
            break
