# pyright: reportAssignmentType=false

import os
from pathlib import Path

import scipy.constants as c
import zntrack as zn
from ase import Atoms, io

from humf_experiments.data.gromacs.read_2_column_xvg import read_xvg_2_column
from humf_experiments.data.gromacs.read_forces_from_gmx_dump import (
    return_forces_from_gmx_dump_of_trj,
)
from humf_experiments.data.gromacs.simplified_gro_reader import (
    NANOMETER_IN_ANGSTROM,
    extract_all_coordinates_from_gro_file,
)
from humf_experiments.nodes.zntrack_utils import SubmititNode, zop


class CreateGromacsDataset(SubmititNode):
    n_h2o_trajectory: str = zn.deps()
    n_h2o_potential_energy: str = zn.deps()
    n_h2o_trajectory_forces: str = zn.deps()

    data_dir: str = zop("data/")

    def do_run(self):
        times, energies = read_xvg_2_column(self.n_h2o_potential_energy)
        forces_df = return_forces_from_gmx_dump_of_trj(
            self.n_h2o_trajectory_forces, splitstring=None
        )
        trajectory = extract_all_coordinates_from_gro_file(
            self.n_h2o_trajectory, itpfile=None
        )
        assert len(times) == len(energies) == len(forces_df) == len(trajectory)

        atoms_list = []
        for frame, energy, atoms_forces_df in zip(
            trajectory, energies, forces_df["atoms_forces_df"]
        ):
            atoms = Atoms(
                symbols=frame.symbols,
                positions=frame.positions * NANOMETER_IN_ANGSTROM,
                info={
                    "energy": energy / c.calorie,
                    "forces": atoms_forces_df[["fx", "fy", "fz"]].to_numpy()
                    / (c.calorie * NANOMETER_IN_ANGSTROM),
                },
            )
            atoms_list.append(atoms)

        raw_dir = Path(self.data_dir) / "raw/"
        os.makedirs(raw_dir, exist_ok=True)
        io.write(str(raw_dir / "dataset.xyz"), atoms_list)
