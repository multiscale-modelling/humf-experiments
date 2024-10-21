# pyright: reportCallIssue=false


import zntrack

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)
from humf_experiments.nodes.create_gromacs_dataset import CreateGromacsDataset
from humf_experiments.nodes.create_orca_dataset import CreateOrcaDataset
from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory


def main():
    project = zntrack.Project(initialize=False)

    with project:
        get_3_h2o_trajectory = NH2OTrajectory(
            num_molecules=2,
            concatenate=50,
            h2o_trajectory_dir="data/h2o_trajectory/",
        )

        CreateGromacsDataset(
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
        CreateOrcaDataset(
            orca_frames_dir=run_orca.output_dir,
        )

        run_orca_2 = ConvertTrajectoryToOrcaInputs(
            name="run_orca_on_manual_oxonium_trajectory",
            method_and_basisset="B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1",
            run_orca=True,
            gro_file="data/water_oxonium_manual_trajectory.gro",
            every_nth_frame=5,
        )
        CreateOrcaDataset(
            name="create_orca_dataset_for_manual_oxonium_trajectory",
            orca_frames_dir=run_orca_2.output_dir,
        )

        # models = ["ljc_water", "polynomial_water"]
        # datasets = [("gromacs", create_gromacs_dataset), ("orca", create_orca_dataset)]
        # for model, dataset in product(models, datasets):
        #     train_model = TrainModel(
        #         name=f"fit_{model}_to_{dataset[0]}",
        #         learning_rate=0.1,
        #         max_epochs=1000,
        #         model=model,
        #         trade_off=1,
        #         data_root_dir=dataset[1].data_dir,
        #     )
        #     EvaluateModels(
        #         name=f"evaluate_{model}_on_{dataset[0]}",
        #         model=model,
        #         data_root_dir=dataset[1].data_dir,
        #         model_dir=train_model.model_dir,
        #     )

    project.build()


if __name__ == "__main__":
    main()
