# pyright: reportAssignmentType=false

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import zntrack as zn

from humf_experiments.nodes.zntrack_utils import zop


class NH2OTrajectory(zn.Node):
    trajectory_gro: str = zn.deps_path()
    trajectory_xtc: str = zn.deps_path()

    num_molecules: int = zn.params()
    concatenate: int = zn.params()

    def run(self):
        trajectory_gro = Path(self.trajectory_gro)
        trajectory_xtc = Path(self.trajectory_xtc)
        assert trajectory_gro.exists()
        assert trajectory_xtc.exists()

        bash_script_path = Path(__file__).parent / "order_and_trj.sh"
        with TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            subprocess.check_output(
                [
                    "bash",
                    bash_script_path,
                    str(self.num_molecules),
                    str(self.concatenate),
                ],
                cwd=tempdir,
            )
