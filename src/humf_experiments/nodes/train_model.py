# pyright: reportAssignmentType=false

import lightning as L
import submitit
import torch
import zntrack as zn
from humf.data.ase_dataset import ASEDataset
from humf.models.force_field import ForceField
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger
from torch_geometric.loader import DataLoader

from humf_experiments.models.factory import create_model
from humf_experiments.nodes.zntrack_utils import zop


class TrainModel(zn.Node):
    batch_size: int = zn.params(32)
    learning_rate: float = zn.params(1e-3)
    max_epochs: int = zn.params(100)
    model: str = zn.params()
    seed: int = zn.params(42)
    trade_off: float = zn.params(0)

    data_root_dir: str = zn.deps()

    log_dir: str = zop("logs/")
    model_dir: str = zop("models/")

    def run(self):
        executor = submitit.AutoExecutor(folder="log_test")
        executor.update_parameters(
            cpus_per_task=8,
            gpus_per_node=1,
            mem_gb=32,
            slurm_partition="a100",
        )
        executor.submit(self._run).result()

    def _run(self):
        torch.set_float32_matmul_precision("high")
        L.seed_everything(self.seed, workers=True)

        model = ForceField(
            create_model(self.model),
            learning_rate=self.learning_rate,
            trade_off=self.trade_off,
        )

        dataset = ASEDataset(self.data_root_dir, force_reload=True)
        dataloader = DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True, num_workers=7
        )

        checkpoint_callback = ModelCheckpoint(
            dirpath=self.model_dir, save_top_k=3, monitor="train/loss"
        )
        # logger = CSVLogger(self.log_dir, name=None)
        logger = TensorBoardLogger(self.log_dir)
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
