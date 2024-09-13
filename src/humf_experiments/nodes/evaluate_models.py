# pyright: reportAssignmentType=false

from pathlib import Path

import pandas as pd
import plotly.express as px
import torch
import zntrack as zn
from humf.data.ase_dataset import ASEDataset
from humf.models.force_field import ForceField

from humf_experiments.models.factory import create_model
from humf_experiments.nodes.zntrack_utils import zop

ENERGY_UNIT = "kcal/mol"
DISTANCE_UNIT = "Å"


class EvaluateModels(zn.Node):
    model: str = zn.params()

    data_root_dir: str = zn.deps()
    model_dir: str = zn.deps()

    results_dir: str = zop("results/")

    def run(self):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        dataset = ASEDataset(self.data_root_dir).to(device)  # type: ignore
        model = create_model(self.model)

        for model_path in Path(self.model_dir).iterdir():
            model_results_dir = Path(self.results_dir) / model_path.stem
            model_results_dir.mkdir(parents=True, exist_ok=True)

            model = ForceField.load_from_checkpoint(
                model_path, energy_model=model
            ).eval()

            with open(model_results_dir / "params.txt", "w") as f:
                for name, params in model.named_parameters():
                    f.write(f"{name}\n{params}\n")

            predicted_energies = []
            predicted_forces = []
            target_energies = []
            target_forces = []
            for data in dataset:
                predictions = model(data)
                predicted_energies.append(predictions[0].item())
                predicted_forces.append(predictions[1].detach().cpu().numpy())
                target_energies.append(data.energy.item())
                target_forces.append(data.forces.detach().cpu().numpy())

            fig = px.scatter(
                x=target_energies,
                y=predicted_energies,
                labels={
                    "x": f"Target energy / {ENERGY_UNIT}",
                    "y": f"Predicted energy / {ENERGY_UNIT}",
                },
                title="Energy prediction",
            )
            fig.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="red", dash="dash"),
                xref="x",
                yref="y",
            )
            fig.write_html(model_results_dir / "energy_prediction.html")

            predicted_forces_df = convert_forces_to_long_dataframe(predicted_forces)
            target_forces_df = convert_forces_to_long_dataframe(target_forces)
            forces_df = pd.merge(
                predicted_forces_df,
                target_forces_df,
                on=["timestep", "atom", "direction"],
                suffixes=("_predicted", "_target"),
            )
            fig = px.scatter(
                forces_df, x="force_target", y="force_predicted", color="direction"
            )
            fig.write_html(model_results_dir / "force_prediction.html")


def convert_forces_to_long_dataframe(data):
    records = []
    for timestep, forces in enumerate(data):
        num_atoms = forces.shape[0]
        for atom in range(num_atoms):
            for direction, force in zip(["x", "y", "z"], forces[atom]):
                records.append(
                    {
                        "timestep": timestep,
                        "atom": atom,
                        "direction": direction,
                        "force": force,
                    }
                )
    df = pd.DataFrame(records)
    return df
