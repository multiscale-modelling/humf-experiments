# pyright: reportAssignmentType=false

import lightning as L
import torch
import zntrack as zn
from humf.data.ase_dataset import ASEDataset
from humf.models.force_field import ForceField
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger
from torch_geometric.loader import DataLoader

from humf_experiments.models.registry import models
from humf_experiments.nodes.zntrack_utils import zop


class TrainModel(zn.Node):
    max_epochs: int = zn.params()
    model: str = zn.params()

    data_root_dir: str = zn.deps()

    log_dir: str = zop("logs/")
    model_dir: str = zop("models/")

    def run(self):
        torch.set_float32_matmul_precision("high")
        L.seed_everything(42, workers=True)

        model = ForceField(
            models[self.model](),
            learning_rate=1e-3,
            trade_off=0.1,
        )

        dataset = ASEDataset(self.data_root_dir, force_reload=True)
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=7)

        checkpoint_callback = ModelCheckpoint(
            dirpath=self.model_dir, save_top_k=5, monitor="train/loss"
        )
        logger = CSVLogger(self.log_dir, name=None)
        trainer = L.Trainer(
            callbacks=[checkpoint_callback],
            deterministic=True,
            enable_progress_bar=False,
            inference_mode=False,
            log_every_n_steps=1,
            logger=logger,
            max_epochs=self.max_epochs,
        )
        trainer.fit(model, dataloader)
