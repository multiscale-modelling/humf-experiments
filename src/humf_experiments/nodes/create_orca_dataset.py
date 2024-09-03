# pyright: reportAssignmentType=false

import os
from pathlib import Path

import zntrack as zn
from ase import Atoms, io

from humf_experiments.data.orca import (
    ANGSTROM_PER_BOHR,
    KCAL_MOL_PER_HARTREE,
    orca_extract_all_frames_from_folder,
)
from humf_experiments.nodes.zntrack_utils import zop


class CreateOrcaDataset(zn.Node):
    orca_frames_dir: str = zn.deps()

    data_dir: str = zop("data/")

    def run(self):
        frames = orca_extract_all_frames_from_folder(self.orca_frames_dir)
        atoms_list = []
        for frame in frames:
            atoms = Atoms(
                symbols=frame["atoms"],
                positions=frame["positions"],
                info={
                    "energy": frame["energy"] * KCAL_MOL_PER_HARTREE,
                    "energy_total": frame["energy_total"] * KCAL_MOL_PER_HARTREE,
                    "forces": frame["forces"]
                    * KCAL_MOL_PER_HARTREE
                    / ANGSTROM_PER_BOHR,
                    "forces_total": frame["forces_total"]
                    * KCAL_MOL_PER_HARTREE
                    / ANGSTROM_PER_BOHR,
                },
            )
            atoms_list.append(atoms)

        raw_dir = Path(self.data_dir) / "raw/"
        os.makedirs(raw_dir, exist_ok=True)
        io.write(str(raw_dir / "dataset.xyz"), atoms_list)
