# pyright: reportCallIssue=false

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
            num_molecules=3,
            concatenate=1,
            h2o_trajectory_dir="data/h2o_trajectory/",
        )
        create_gromacs_dataset = CreateGromacsDataset(
            n_h2o_trajectory=get_3_h2o_trajectory.n_h2o_trajectory,
            n_h2o_potential_energy=get_3_h2o_trajectory.n_h2o_potential_energy,
            n_h2o_trajectory_forces=get_3_h2o_trajectory.n_h2o_trajectory_forces,
        )
        fit_model_to_gromacs_data = TrainModel(
            data_root_dir=create_gromacs_dataset.data_dir,
            max_epochs=1000,
        )
        EvaluateModels(
            data_root_dir=create_gromacs_dataset.data_dir,
            model_dir=fit_model_to_gromacs_data.model_dir,
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
        create_orca_dataset = CreateOrcaDataset(
            orca_frames_dir=run_orca.output_dir,
        )
        train_model = TrainModel(
            data_root_dir=create_orca_dataset.data_dir,
            max_epochs=1000,
        )
        EvaluateModels(
            data_root_dir=create_orca_dataset.data_dir,
            model_dir=train_model.model_dir,
        )

    project.build()


if __name__ == "__main__":
    main()
