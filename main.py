# pyright: reportCallIssue=false

import zntrack

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)
from humf_experiments.nodes.create_orca_dataset import CreateOrcaDataset
from humf_experiments.nodes.evaluate_models import EvaluateModels
from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory
from humf_experiments.nodes.train_model import TrainModel


def main():
    project = zntrack.Project(
        initialize=False,
        automatic_node_names=False,
        magic_names=True,
    )

    with project:
        get_3_h2o_trajectory = NH2OTrajectory(
            num_molecules=3,
            concatenate=1,
            h2o_trajectory_dir="data/h2o_trajectory/",
        )
        run_orca = ConvertTrajectoryToOrcaInputs(
            method_and_basisset="B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1",
            run_orca=True,
            gro_file=get_3_h2o_trajectory.n_h2o_trajectory,
            every_nth_frame=10,
        )
        create_dataset = CreateOrcaDataset(
            orca_frames_dir=run_orca.output_dir,
        )
        train_model = TrainModel(
            data_root_dir=create_dataset.data_dir,
            max_epochs=10,
        )
        evaluate_models = EvaluateModels(
            data_root_dir=create_dataset.data_dir,
            model_dir=train_model.model_dir,
        )

        # `magic_names=True` requires nodes to be assigned to a named variable, but
        # pre-commit using Ruff fails if there are unused variables. To avoid this,
        # we just print the last node here.
        print(f"[Ignore this line. {evaluate_models}]")

    project.build()


if __name__ == "__main__":
    main()
