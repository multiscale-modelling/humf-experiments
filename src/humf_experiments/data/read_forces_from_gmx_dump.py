### the following is directly copied from the old dataloader ondisk_gmx.py which does everything in one go and combines the resutls
# now only the forces are desired here you go:
import io

import pandas as pd


def parse_forces_section_gmx(section):
    debug = False
    lines = section.split("\n")
    timestep = int(lines[1].split()[3])
    time = float(lines[1].split()[4].replace("time=", ""))

    atomnumber = int(lines[1].split()[1])  # redundant - nur zum debuggen verwendet
    if debug:
        print("atomnumber", atomnumber)
    atoms_data_forces = lines[7:]
    atoms_forces_df = pd.read_csv(
        io.StringIO(
            "\n".join(atoms_data_forces)
            .replace("f[", "")
            .replace("]", "")
            .replace("{", "")
            .replace("}", "")
            .replace(",", " ")
            .replace("=", " ")
        ),
        sep=r"\s+",
        names=["nr", "fx", "fy", "fz"],
    )
    return timestep, atoms_forces_df, time


def read_dumped_trr(filename, headerstr):
    with open(filename, "r") as f:
        forces_sections = f.read().split(headerstr)
        forces_data = [
            parse_forces_section_gmx(forces_sections[s])
            for s in range(1, len(forces_sections))
        ]
        forces_data_df = pd.DataFrame(
            forces_data, columns=["timestep", "atoms_forces_df", "time"]
        )
    return forces_data_df


def return_forces_from_gmx_dump_of_trj(dumpfilename, splitstring):
    """
    Read a dump file from gmx trjconv -f file.trr -s file.tpr -o file.dump
    and return the forces as a list of numpy arrays - you need to use the correct string at which the file is split into frames
    this is identical to the name of the trajectory file
    in the case of my script for the reruns : tmp.trr
    however if you rename it change it
    or use the function find_splitstring to find it
    """
    if splitstring is None:
        print("using default tmp.trr as the splitstring")
        print(
            "if this is not the correct string use the function find_splitstring to find it"
        )

    forces_df = read_dumped_trr(dumpfilename, splitstring)
    return forces_df


def find_splitstring(filename):
    """
    Find the string at which the file is split into frames
    this is identical to the name of the trajectory file
    in the case of my script for the reruns : tmp.trr
    however if you rename it change it
    """
    with open(filename, "r") as f:
        for line in f:
            if "trr" in line:
                trythis = line.split(sep=".trr")[0].split()[-1]
                return trythis + ".trr"
