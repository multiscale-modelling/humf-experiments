# pyright: reportAssignmentType=false

import os
import subprocess
from pathlib import Path

import zntrack as zn

from humf_experiments.nodes.zntrack_utils import zop


def run_which(command):
    try:
        result = subprocess.check_output(["which", command], universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError:
        return None


def run_orca_on_file(orca_bin, file, outfile):
    print("starting orca process")
    with open(outfile, "w") as of:
        subprocess.Popen([orca_bin, file], stdout=of, stderr=subprocess.STDOUT)


class ConvertTrajectoryToOrcaInputs(zn.Node):
    method_and_basisset: str = zn.params()
    multiplicity: str = zn.params()
    charge: str = zn.params()
    pal: str = zn.params()
    run_orca: bool = zn.params()
    every_nth_frame: int = zn.params()

    gro_file: str = zn.deps()

    output_dir: str = zop("frames/")

    def run(self):
        print("am I running orca", self.run_orca)
        print("operating on the gro File")
        print(self.gro_file)
        print("using every ", self.every_nth_frame, "th frame")
        assert Path(self.gro_file).resolve().is_file()
        orca_bin = run_which("orca")
        if orca_bin is None:
            print("no ORCA in PATH - only generating input")
            self.run_orca = False
        with open(self.gro_file, "r") as gro:
            lines = gro.readlines()
            frame_start = 0
            frame_count = 0
            while frame_start < len(lines):
                atom_count = int(lines[frame_start + 1])
                frame_end = frame_start + atom_count + 3
                if frame_count % self.every_nth_frame == 0:
                    frame_dir = os.path.join(
                        self.output_dir, f"frame_{frame_count // self.every_nth_frame}"
                    )
                    os.makedirs(frame_dir, exist_ok=True)
                    residues = {}
                    all_atoms = []
                    for line in lines[frame_start + 2 : frame_end - 1]:
                        residue_id = int(line[:5])
                        atom_name = line[10:15].strip()
                        if atom_name == "OW":
                            atom_name = "O"
                        elif atom_name in ["HW1", "HW2"]:
                            atom_name = "H"
                        x, y, z = line[20:28], line[28:36], line[36:44]
                        if residue_id not in residues:
                            residues[residue_id] = []
                        residues[residue_id].append((atom_name, x, y, z))
                        all_atoms.append((atom_name, x, y, z))
                    orcacommand_full = (
                        "! "
                        + self.method_and_basisset
                        + " EnGrad\n%PAL NPROCS "
                        + str(self.pal)
                        + " END  \n\n* xyz "
                        + self.charge
                        + " "
                        + self.multiplicity
                        + " \n"
                    )
                    with open(os.path.join(frame_dir, "input_all.inp"), "w") as inp:
                        inp.write(orcacommand_full)
                        for atom_name, x, y, z in all_atoms:
                            inp.write(f"{atom_name} {x} {y} {z}\n")
                        inp.write("*")
                    if self.run_orca:
                        run_orca_on_file(
                            orca_bin,
                            os.path.join(frame_dir, "input_all.inp"),
                            os.path.join(frame_dir, "orca_output.txt"),
                        )

                    for residue_id, atoms in residues.items():
                        residue_dir = os.path.join(frame_dir, f"residue_{residue_id}")
                        os.makedirs(residue_dir, exist_ok=True)
                        with open(os.path.join(residue_dir, "input.inp"), "w") as inp:
                            orcacommand = (
                                "! "
                                + self.method_and_basisset
                                + " EnGrad\n%PAL NPROCS "
                                + str(self.pal)
                                + " END  \n\n* xyz "
                                + self.charge
                                + " "
                                + self.multiplicity
                                + " \n"
                            )
                            inp.write(orcacommand)
                            #                        inp.write("! B3LYP def2-TZVP D3BJ EnGrad\n\n* xyz 0 1\n")
                            for atom_name, x, y, z in atoms:
                                inp.write(f"{atom_name} {x} {y} {z}\n")
                            inp.write("*")
                        if self.run_orca:
                            run_orca_on_file(
                                orca_bin,
                                os.path.join(residue_dir, "input.inp"),
                                os.path.join(residue_dir, "orca_output.txt"),
                            )
                frame_start = frame_end
                frame_count += 1
        print("to analyze:", frame_count // self.every_nth_frame, "frames")
