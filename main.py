# pyright: reportCallIssue=false

import zntrack

from humf_experiments.nodes.convert_trajectory_to_orca_inputs import (
    ConvertTrajectoryToOrcaInputs,
)
from humf_experiments.nodes.n_h2o_trajectory import NH2OTrajectory


def main():
    project = zntrack.Project(
        initialize=False,
        remove_existing_graph=True,
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

        # `magic_names=True` requires nodes to be assigned to a named variable, but
        # pre-commit using Ruff fails if there are unused variables. To avoid this,
        # we just print the last node here.
        print(run_orca)

    project.build()


if __name__ == "__main__":
    main()
