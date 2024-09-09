# pyright: reportCallIssue=false


from humf.data.ase_dataset import ASEDataset

from humf_experiments.nodes.create_gromacs_dataset import CreateGromacsDataset
from humf_experiments.old.gmx_dataset import GMXDataset


class TestCreateGromacsDataset:
    def test_run(self):
        node = CreateGromacsDataset(
            n_h2o_trajectory="inputs/create_gromacs_dataset/gromacs/data/raw/reduced.gro",
            n_h2o_potential_energy="inputs/create_gromacs_dataset/gromacs/data/raw/energy.xvg",
            n_h2o_trajectory_forces="inputs/create_gromacs_dataset/gromacs/data/raw/dumped_forces.txt",
        )
        node.run()

    def test_equal_to_old_dataset(self):
        ase_dataset = ASEDataset(
            root="inputs/create_gromacs_dataset/ase/data", force_reload=True
        )
        gmx_dataset = GMXDataset(
            cutoff=1.0,
            root="inputs/create_gromacs_dataset/gromacs/data",
        )
        assert len(ase_dataset) == len(gmx_dataset)
        for ase_data, gmx_data in zip(ase_dataset, gmx_dataset):
            assert ase_data.pos.allclose(gmx_data.pos)
            assert ase_data.types.allclose(gmx_data.z)
            assert ase_data.energy.allclose(gmx_data.y.squeeze(1), rtol=1e-3)
            assert ase_data.forces.allclose(gmx_data.x.squeeze(1), rtol=1e-3)
