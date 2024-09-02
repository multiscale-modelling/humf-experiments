# pyright: reportAssignmentType=false

import lightning as L
import torch
import zntrack as zn
from humf.data.ase_dataset import ASEDataset
from humf.layers.energy.tip3p_like import Tip3pLike
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

        model = ForceField(
            Tip3pLike(),
            learning_rate=1e-3,
            trade_off=0.1,
        )

        dataset = ASEDataset(self.data_root_dir, force_reload=True)
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
