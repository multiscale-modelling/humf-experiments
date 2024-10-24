# pyright: reportCallIssue=false

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)


class TestConvertTrajectoryToOrcaInputs:
    def test_run_without_orca(self):
        node = ConvertTrajectoryToOrcaInputs(
            method_and_basisset="B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1",
            run_orca=False,
            gro_file="inputs/convert_trajectory_to_orca_inputs/reduced.gro",
            every_nth_frame=10,
        )
        node.run()
