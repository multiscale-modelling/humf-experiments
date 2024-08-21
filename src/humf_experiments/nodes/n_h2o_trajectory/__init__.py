import os
import subprocess
from pathlib import Path

import zntrack as zn

from humf_experiments.nodes.zntrack_utils import zop


class NH2OTrajectory(zn.Node):
    trajectory_gro: str = zn.deps_path()  # pyright: ignore[reportAssignmentType]
    trajectory_xtc: str = zn.deps_path()  # pyright: ignore[reportAssignmentType]

    def run(self):
        trajectory_gro = Path(self.trajectory_gro)
        trajectory_xtc = Path(self.trajectory_xtc)
        assert trajectory_gro.exists()
        assert trajectory_xtc.exists()
        bash_script_path = Path(__file__).parent / "order_and_trj.sh"
        subprocess.run(["bash", bash_script_path])
