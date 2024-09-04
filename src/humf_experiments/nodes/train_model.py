# pyright: reportAssignmentType=false

import lightning as L
import numpy as np
import torch
import zntrack as zn
from humf.data.ase_dataset import ASEDataset
from humf.data.utils import has_nans
from humf.layers.energy.lennard_jones_coulomb import LennardJonesCoulomb
from humf.layers.interaction_sites.atom_centered_static import AtomCenteredStatic
from humf.models.force_field import ForceField
from lightning.pytorch.loggers import WandbLogger
from torch_geometric.loader import DataLoader

from humf_experiments.nodes.zntrack_utils import zop


class TrainModel(zn.Node):
    max_epochs: int = zn.params()

    data_root_dir: str = zn.deps()

    model_path: str = zop("model.ckpt")

    def run(self):
        torch.set_float32_matmul_precision("high")
        L.seed_everything(42, workers=True)

        initial_lj_params = np.array([[0.1521, 3.1507], [0.0, 1.0], [0.0, 1.0]])
        lennard_jones_sites = AtomCenteredStatic(
            num_atoms_per_mol=3,
            num_params_per_atom=2,
            initial_params=torch.tensor(initial_lj_params),
        )

        initial_charges = np.array([[-1.0], [0.5], [0.5]])
        coulomb_sites = AtomCenteredStatic(
            num_atoms_per_mol=3,
            num_params_per_atom=1,
            initial_params=torch.tensor(initial_charges),
        )

        model = ForceField(
            LennardJonesCoulomb(lennard_jones_sites, coulomb_sites),
            learning_rate=1e-3,
            trade_off=0.1,
        )

        dataset = ASEDataset(self.data_root_dir, force_reload=True)
        for data in dataset:
            if has_nans(data):
                raise ValueError("Data contains NaNs")
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=7)

        logger = WandbLogger(project="humf-experiments")
        trainer = L.Trainer(
            deterministic=True,
            enable_checkpointing=False,
            enable_progress_bar=False,
            inference_mode=False,
            log_every_n_steps=1,
            logger=logger,
            max_epochs=self.max_epochs,
        )
        trainer.fit(model, dataloader)
        trainer.save_checkpoint(self.model_path)
