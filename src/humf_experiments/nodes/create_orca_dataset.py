# pyright: reportAssignmentType=false

import os
from pathlib import Path

import zntrack as zn
from ase import Atoms, io

from humf_experiments.data.orca import orca_extract_all_frames_from_folder
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
                    "energy": frame["energy"],
                    "energy_total": frame["energy_total"],
                    "forces": frame["forces"],
                    "forces_total": frame["forces_total"],
                },
            )
            atoms_list.append(atoms)

        raw_dir = Path(self.data_dir) / "raw/"
        os.makedirs(raw_dir, exist_ok=True)
        io.write(str(raw_dir / "dataset.xyz"), atoms_list)
