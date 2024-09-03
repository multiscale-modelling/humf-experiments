import os

import numpy as np

KCAL_MOL_PER_HARTREE = 627.50947406
ANGSTROM_PER_BOHR = 0.529177208


def find_energy_in_orca_output(filename):
    """
    Find the energy in an ORCA output file of a single point calculation.
    File format as used of orca 6.0.0
    """
    with open(filename) as f:
        for line in f:
            if "FINAL SINGLE POINT ENERGY" in line:
                return float(line.split()[-1])
        raise ValueError("Energy not found in ORCA output file")


def orca_check_normal_termination(filename):
    """
    Check if the ORCA calculation terminated normally.
    """
    with open(filename) as f:
        for line in f:
            if "ORCA TERMINATED NORMALLY" in line:
                return True
        return False


def orca_find_forces(filename, natoms_in_mol):
    """
    Find the forces in an ORCA output file of a single point calculation.
    File format as used of orca 6.0.0
    """
    forces = []
    atoms = []
    index = []
    with open(filename, "r") as f:
        for line in f:
            if "CARTESIAN GRADIENT" in line:
                # print("starting to read forces")
                # skip 2 lines (-------- seperator and empty line)
                for _ in range(2):
                    line = next(f)
                # read forces
                for _ in range(natoms_in_mol):
                    line = next(f)
                    vals = line.split()

                    forces.append([float(x) for x in vals[3:6]])
                    atoms.append(vals[1])
                    index.append(int(vals[0]))
                return atoms, index, forces
            # if end of file is reached without finding the forces raise error
        raise ValueError("Forces not found in ORCA output file")


def orca_get_number_of_atoms(filename):
    """
    Get the number of atoms in a molecule from an ORCA output file.
    """
    with open(filename) as f:
        for line in f:
            if "Number of atoms" in line:
                return int(line.split()[-1])
        raise ValueError("Number of atoms not found in ORCA output file")


def orca_extract_coordinates(filename, natoms_in_mol):
    """
    Find the coordinates in an ORCA output file of a single point calculation.
    File format as used of orca 6.0.0
    """
    coordinates = []
    atoms = []

    with open(filename, "r") as f:
        for line in f:
            if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
                # print("starting to read coordinates")
                # skip 2 lines (-------- seperator but no empty line)
                for _ in range(1):
                    line = next(f)
                # read coordinates
                for _ in range(natoms_in_mol):
                    line = next(f)
                    vals = line.split()

                    coordinates.append([float(x) for x in vals[1:4]])
                    atoms.append(vals[0])

                return atoms, coordinates
            # if end of file is reached without finding the forces raise error
        raise ValueError("Coordinates not found in ORCA output file")


def extract_orca_output(filename):
    """
    first check whether the calculation terminated normally
    then extract the energy and forces
    for the forces first get the number of atoms in the molecule
    """
    if orca_check_normal_termination(filename):
        natoms_in_mol = int(orca_get_number_of_atoms(filename))
        energy = float(find_energy_in_orca_output(filename))
        atoms, index, forces = orca_find_forces(filename, natoms_in_mol)
        atoms2, coordinates = orca_extract_coordinates(filename, natoms_in_mol)
        assert atoms == atoms2
        # print(atoms, atoms2)
        return atoms, index, energy, coordinates, forces
    else:
        raise ValueError("ORCA calculation did not terminate normally")


def extract_orca_frame(foldername, output_name):
    """
    in the folder the file for the whole system but also multiple other folders for subsystems are present
    extract_orca_output for the whole system and do the same for each subsystem
    then subtract the forces and energies of the subsystems from the whole system
    - for the forces only on the appropriate atoms
    - for the energies just subtract the energy of the subsystem from the whole system
    returns the atoms, energy, corrected energy, total forces and corrected forces
    """
    # fist check whether folder exists
    if not os.path.exists(foldername):
        raise ValueError("Folder does not exist")
    # check whether the output file exists in the folder
    if not os.path.exists(foldername + "/" + output_name):
        raise ValueError("Output file does not exist")
    # extract the whole system
    atoms, _, energy, coordinates, forces = extract_orca_output(
        foldername + "/" + output_name
    )
    # find all subsystems
    subsystems = [x[0] for x in os.walk(foldername)]
    # remove the first element which is the folder itself
    subsystems = subsystems[1:]
    # as the subsystems are ordered by the integer at the end of the folder name, sort them
    subsystems.sort(key=lambda x: int(x.split("residue_")[-1]))
    # iterate over all subsystems - start with the fist one and subtract the forces and energies in a running manner
    # where the current atoms of the subsystem are subsequent slices of the atoms from the whole system
    # therefore check whether the coordinates are equal
    energy_for_subtraction = energy
    forces = np.array(forces)
    forces_for_subtraction = forces.copy()
    index_offset = 0
    atoms = np.array(atoms)
    coordinates = np.array(coordinates)

    for subfolder in subsystems:
        # extract the subsystem
        atoms_sub, index_sub, energy_sub, coordinates_sub, forces_sub = (
            extract_orca_output(subfolder + "/" + output_name)
        )
        index_current = [
            index_sub[i] + index_offset - 1 for i in range(len(index_sub))
        ]  # index starts at 1 for atoms

        for i in range(len(atoms_sub)):
            assert atoms[index_current[i]] == atoms_sub[i]
            for j in range(3):
                assert coordinates[index_current[i]][j] == coordinates_sub[i][j]

                forces_for_subtraction[index_current[i]][j] -= forces_sub[i][j]

        index_offset += len(index_sub)

        energy_for_subtraction -= energy_sub

    # forces for examples recalculated by hand - correkt!
    return (
        atoms,
        energy,
        energy_for_subtraction,
        forces,
        forces_for_subtraction,
        coordinates,
    )


def orca_extract_all_frames_from_folder(
    working_folder,
    prefix_frames: str = "frame_",
    orca_outputs_name: str = "orca_output.txt",
) -> list[dict[str, np.ndarray]]:
    results_list = []
    if not os.path.exists(working_folder):
        raise ValueError("Folder does not exist")
    # find all frames
    frames = [
        os.path.join(working_folder, x)
        for x in os.listdir(working_folder)
        if os.path.isdir(os.path.join(working_folder, x))
    ]
    # as the frames are ordered by the integer at the end of the folder name, sort them
    frames.sort(key=lambda x: int(x.split(prefix_frames)[-1]))
    for frame in frames:
        print("importing frame", frame)
        atoms, energy, energy_subtracted, forces, forces_subtracted, coordinates = (
            extract_orca_frame(frame, orca_outputs_name)
        )
        tmp_dict = {
            "energy": np.array(energy_subtracted),
            "forces": np.array(forces_subtracted),
            "atoms": np.array(atoms),
            "energy_total": np.array(energy),
            "forces_total": np.array(forces),
            "positions": np.array(coordinates),
        }
        results_list.append(tmp_dict)
    return results_list
