# pyright: reportAssignmentType=false

import lightning as L
import torch
import zntrack as zn
from dvclive.lightning import DVCLiveLogger
from humf.data.ase_dataset import ASEDataset
from humf.models.force_field import ForceField
from lightning.pytorch.callbacks import ModelCheckpoint
from torch_geometric.loader import DataLoader

from humf_experiments.models.factory import create_model
from humf_experiments.nodes.zntrack_utils import SubmititNode, zop


class TrainModel(SubmititNode):
    batch_size: int = zn.params(32)
    learning_rate: float = zn.params(1e-3)
    max_epochs: int = zn.params(100)
    model: str = zn.params()
    seed: int = zn.params(42)
    trade_off: float = zn.params(0)

    data_root_dir: str = zn.deps()

    live_dir: str = zop("dvclive/")
    model_dir: str = zop("models/")

    def get_executor_parameters(self):
        return {
            "cpus_per_task": 8,
            "gpus_per_node": 1,
            "mem_gb": 32,
            "slurm_partition": "a100",
            "timeout_min": 8 * 60,
        }

    def do_run(self):
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
        logger = DVCLiveLogger(
            dir=self.live_dir, dvcyaml=str(self.nwd / "dvc.yaml"), save_dvc_exp=False
        )
        trainer = L.Trainer(
            callbacks=[checkpoint_callback],
            deterministic=True,
            enable_progress_bar=False,
            inference_mode=False,
            log_every_n_steps=len(dataloader) // 2 + 1,
            logger=logger,
            max_epochs=self.max_epochs,
        )
        trainer.fit(model, dataloader)
