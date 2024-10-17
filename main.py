# pyright: reportCallIssue=false

from itertools import product

import zntrack

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)
from humf_experiments.nodes.create_gromacs_dataset import CreateGromacsDataset
from humf_experiments.nodes.create_orca_dataset import CreateOrcaDataset
from humf_experiments.nodes.evaluate_models import EvaluateModels
from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory
from humf_experiments.nodes.train_model import TrainModel


def main():
    project = zntrack.Project(initialize=False)

    with project:
        get_3_h2o_trajectory = NH2OTrajectory(
            num_molecules=2,
            concatenate=50,
            h2o_trajectory_dir="data/h2o_trajectory/",
        )

        create_gromacs_dataset = CreateGromacsDataset(
            n_h2o_trajectory=get_3_h2o_trajectory.n_h2o_trajectory,
            n_h2o_potential_energy=get_3_h2o_trajectory.n_h2o_potential_energy,
            n_h2o_trajectory_forces=get_3_h2o_trajectory.n_h2o_trajectory_forces,
        )

        run_orca = ConvertTrajectoryToOrcaInputs(
            method_and_basisset="B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1",
            run_orca=True,
            gro_file=get_3_h2o_trajectory.n_h2o_trajectory,
            every_nth_frame=5,
        )
        create_orca_dataset = CreateOrcaDataset(
            orca_frames_dir=run_orca.output_dir,
        )

        models = ["ljc_water", "polynomial_water"]
        datasets = [("gromacs", create_gromacs_dataset), ("orca", create_orca_dataset)]
        for model, dataset in product(models, datasets):
            train_model = TrainModel(
                name=f"fit_{model}_to_{dataset[0]}",
                learning_rate=0.1,
                max_epochs=1000,
                model=model,
                trade_off=1,
                data_root_dir=dataset[1].data_dir,
            )
            EvaluateModels(
                name=f"evaluate_{model}_on_{dataset[0]}",
                model=model,
                data_root_dir=dataset[1].data_dir,
                model_dir=train_model.model_dir,
            )

    project.build()


if __name__ == "__main__":
    main()
