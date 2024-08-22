# pyright: reportCallIssue=false

import shutil

import pytest

from humf_experiments.nodes.gen_orca_inputs_from_trajectory import convert_trj_to_individual_orca_inputs



class Test_convert_trj_to_individual_orca_inputs:
    def test_run(self):
        node = convert_trj_to_individual_orca_inputs(
            method_and_basisset=" B3LYP def2-TZVP D3BJ",
            multiplicity="1",
            charge="0",
            pal="1", 
            run_orca=False,
            output_dir="tests/outputs/orca_superdir",
            gro_file="tests/inputs/orca_runfile_generation/reduced.gro", # "n_h2o_trajectory_dir/reduced.gro",
            every_nth_frame=10, 
)
        node.run()
