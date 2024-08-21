# pyright: reportCallIssue=false

from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory


class TestNH2OTrajectory:
    def test_run(self):
        node = NH2OTrajectory(
            trajectory_gro="tests/inputs/n_h2o_trajectory/trajectory.gro",
            trajectory_xtc="tests/inputs/n_h2o_trajectory/trajectory.xtc",
        )
        node.run()
