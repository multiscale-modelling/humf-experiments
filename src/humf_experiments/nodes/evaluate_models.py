# pyright: reportAssignmentType=false

from pathlib import Path

import pandas as pd
import plotly.express as px
import torch
import zntrack as zn
from dvclive.live import Live
from humf.data.ase_dataset import ASEDataset
from humf.models.force_field import ForceField

from humf_experiments.models.factory import create_model
from humf_experiments.nodes.zntrack_utils import SubmititNode, zop

ENERGY_UNIT = "kcal/mol"
DISTANCE_UNIT = "Å"


class EvaluateModels(SubmititNode):
    model: str = zn.params()

    data_root_dir: str = zn.deps()
    model_dir: str = zn.deps()

    live_dir: str = zop("dvclive/")
    results_dir: str = zop("results/")

    def get_executor_parameters(self):
        return {
            "cpus_per_task": 8,
            "gpus_per_node": 1,
            "mem_gb": 32,
            "slurm_partition": "a100",
            "timeout_min": 8 * 60,
        }

    def do_run(self):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        dataset = ASEDataset(self.data_root_dir).to(device)  # type: ignore
        results_dir = Path(self.results_dir)

        with Live(dir=self.live_dir, dvcyaml=str(self.nwd / "dvc.yaml")) as live:
            for model_path in Path(self.model_dir).iterdir():
                model_results_dir = results_dir / model_path.stem
                model_results_dir.mkdir(parents=True, exist_ok=True)

                model = ForceField.load_from_checkpoint(
                    model_path, energy_model=create_model(self.model)
                ).eval()

                evaluate_model(model, dataset, model_results_dir, live)


def evaluate_model(model, dataset, model_results_dir, live):
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
        title="Energy prediction",
        labels={
            "x": f"Target energy / {ENERGY_UNIT}",
            "y": f"Predicted energy / {ENERGY_UNIT}",
        },
    )
    fig.add_shape(**get_line_of_equality(target_energies, predicted_energies))
    fig.write_html(model_results_dir / "energy_prediction.html")
    fig.write_image(model_results_dir / "energy_prediction.png")
    live.log_image("energy prediction", model_results_dir / "energy_prediction.png")

    predicted_forces_df = convert_forces_to_long_dataframe(predicted_forces)
    target_forces_df = convert_forces_to_long_dataframe(target_forces)
    forces_df = pd.merge(
        predicted_forces_df,
        target_forces_df,
        on=["timestep", "atom", "direction"],
        suffixes=("_predicted", "_target"),
    )
    fig = px.scatter(
        forces_df,
        x="force_target",
        y="force_predicted",
        color="direction",
        title="Force prediction",
        labels={
            "force_target": f"Target force / {ENERGY_UNIT}/{DISTANCE_UNIT}",
            "force_predicted": f"Predicted force / {ENERGY_UNIT}/{DISTANCE_UNIT}",
            "direlection": "Direction",
        },
    )
    fig.add_shape(
        **get_line_of_equality(forces_df["force_target"], forces_df["force_predicted"])
    )
    fig.write_html(model_results_dir / "force_prediction.html")
    fig.write_image(model_results_dir / "force_prediction.png")
    live.log_image("force prediction", model_results_dir / "force_prediction.png")


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


def get_line_of_equality(x, y):
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    minimum = min(x_min, y_min)
    maximum = max(x_max, y_max)
    return {
        "type": "line",
        "line": {"color": "red", "dash": "dash"},
        "x0": minimum,
        "y0": minimum,
        "x1": maximum,
        "y1": maximum,
    }
