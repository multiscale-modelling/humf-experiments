# pyright: reportCallIssue=false


from humf_experiments.nodes.create_gromacs_dataset import CreateGromacsDataset


class TestCreateGromacsDataset:
    def test_run(self):
        node = CreateGromacsDataset(
            n_h2o_trajectory="inputs/create_gromacs_dataset/reduced.gro",
            n_h2o_potential_energy="inputs/create_gromacs_dataset/energy.xvg",
            n_h2o_trajectory_forces="inputs/create_gromacs_dataset/dumped_forces.txt",
        )
        node.run()
