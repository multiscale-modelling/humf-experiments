# pyright: reportCallIssue=false

import shutil

import pytest

from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory


@pytest.fixture(scope="module", autouse=True)
def check_gmx_command():
    if shutil.which("gmx") is None:
        pytest.skip("Skipping test: 'gmx' command not found.")


class TestNH2OTrajectory:
    def test_run(self):
        node = NH2OTrajectory(
            num_molecules=3,
            concatenate=1,
            h2o_trajectory_dir="tests/inputs/h2o_trajectory",
        )
        node.run()
