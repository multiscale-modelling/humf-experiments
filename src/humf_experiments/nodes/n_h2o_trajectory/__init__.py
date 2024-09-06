# pyright: reportAssignmentType=false

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import zntrack as zn

from humf_experiments.nodes.zntrack_utils import zop


class NH2OTrajectory(zn.Node):
    num_molecules: int = zn.params()
    concatenate: int = zn.params()

    h2o_trajectory_dir: str = zn.deps_path()

    n_h2o_trajectory: str = zop("reduced.gro")

    def run(self):
        os.makedirs(self.nwd, exist_ok=True)
        bash_script_path = Path(__file__).parent / "order_and_trj.sh"
        trajectory_dir = Path(self.h2o_trajectory_dir).resolve()
        assert trajectory_dir.is_dir()

        with TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            # Gromacs includes the itp file from the working directory.
            shutil.copy(trajectory_dir / "tip3p.itp", tempdir)
            subprocess.check_output(
                [
                    "bash",
                    bash_script_path,
                    trajectory_dir,
                    str(self.num_molecules),
                    str(self.concatenate),
                ],
                cwd=tempdir,
            )
            shutil.copy(tempdir / "reduced.gro", self.n_h2o_trajectory)
