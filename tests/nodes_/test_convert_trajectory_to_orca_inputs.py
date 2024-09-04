# pyright: reportCallIssue=false

import shutil

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)


def orca_is_available():
    return shutil.which("orca") is not None


class TestConvertTrajectoryToOrcaInputs:
    def test_run_without_orca(self):
        node = ConvertTrajectoryToOrcaInputs(
            method_and_basisset="B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1",
            run_orca=False,
            gro_file="inputs/orca_runfile_generation/reduced.gro",
            every_nth_frame=10,
        )
        node.run()
