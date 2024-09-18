# pyright: reportAssignmentType=false

import os
from pathlib import Path

import zntrack as zn
from ase import Atoms, io

from humf_experiments.data.orca import (
    BOHR_IN_ANGSTROM,
    HARTREE_IN_KCAL_PER_MOL,
    orca_extract_all_frames_from_folder,
)
from humf_experiments.nodes.zntrack_utils import SubmititNode, zop


class CreateOrcaDataset(SubmititNode):
    orca_frames_dir: str = zn.deps()

    data_dir: str = zop("data/")

    def do_run(self):
        frames = orca_extract_all_frames_from_folder(self.orca_frames_dir)
        atoms_list = []
        for frame in frames:
            # Saves positions in Angstrom, energies in kcal/mol,
            # and forces in kcal/mol/Angstrom
            atoms = Atoms(
                symbols=frame["atoms"],
                positions=frame["positions"],
                info={
                    "energy": frame["energy"] * HARTREE_IN_KCAL_PER_MOL,
                    "energy_total": frame["energy_total"] * HARTREE_IN_KCAL_PER_MOL,
                    "forces": frame["forces"]
                    * HARTREE_IN_KCAL_PER_MOL
                    / BOHR_IN_ANGSTROM,
                    "forces_total": frame["forces_total"]
                    * HARTREE_IN_KCAL_PER_MOL
                    / BOHR_IN_ANGSTROM,
                },
            )
            atoms_list.append(atoms)

        raw_dir = Path(self.data_dir) / "raw/"
        os.makedirs(raw_dir, exist_ok=True)
        io.write(str(raw_dir / "dataset.xyz"), atoms_list)
