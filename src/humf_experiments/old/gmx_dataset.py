import io

import numpy as np
import pandas as pd
import torch
from ase import Atoms
from matscipy.neighbours import neighbour_list  # , find_common_neighbours
from torch_geometric.data import (  # as an alternative to InMemoryDataset,
    Data,
    OnDiskDataset,
)

debug = False


class GMXDataset(OnDiskDataset):
    def __init__(
        self,
        root,
        cutoff,
        transform=None,
        pre_transform=None,
        pre_filter=None,
        backend="sqlite",
        raw_file_names=["reduced.gro", "energy.xvg", "dumped_forces.txt"],
        splitstring_gro="tip3p box",
        splitstring_forces="tmp.trr",
    ):
        self.cutoff = cutoff
        self._raw_file_names = raw_file_names
        self.splitstring_gro = splitstring_gro
        self.splitstring_forces = splitstring_forces
        super().__init__(root, transform, pre_transform, backend)
        # no load here as in InMemoryDataset

    @property
    def raw_file_names(self):
        return self._raw_file_names

    @raw_file_names.setter
    def raw_file_names(self, value):
        self._raw_file_names = value
        print.self_raw_file_names

    @property
    def processed_file_names(self):
        return ["dataset_g.pt"]

    # @mprof
    def process(self):
        print("processing")
        print(self.raw_paths)

        print("splitstring", "tip3p box")
        trajectory_data_df = read_dumped_trajectory(
            self.raw_paths[0], self.splitstring_gro
        )
        # funktioniert bis hier
        print("traj_data", trajectory_data_df.head())

        forces_df = read_dumped_trr(self.raw_paths[2], self.splitstring_forces)
        print("forces_df", forces_df.head())
        energy_df = pd.read_csv(
            self.raw_paths[1],
            sep=r"\s+",
            comment="#",
            skiprows=24,
            names=["time", "energy"],
        )
        merged_df1 = trajectory_data_df.merge(energy_df, on="time")
        merged_df = merged_df1.merge(forces_df, on="time")

        for row in merged_df.drop(
            ["timestep_x", "timestep_y", "time"], axis=1
        ).itertuples(index=False):
            tmp = get_data_gmx(*row, cutoff=self.cutoff)
            # depending on whether the data is filtered and/or transformed
            if self.pre_filter is not None:
                if self.pre_filter(tmp):
                    if self.pre_transform is not None:
                        self.append(self.pre_transform(tmp))
                    else:
                        self.append(tmp)
                else:
                    pass
            elif self.pre_transform is not None and self.pre_filter is None:
                self.append(self.pre_transform(tmp))
            else:
                self.append(tmp)


# @mprof
def parse_trajectory_section_gmx(section):
    lines = section.split("\n")
    timestep = int(lines[0].split()[-1])
    time = float(lines[0].split()[-3])
    atomnumber = int(lines[1])

    cell = [10 * float(lines[atomnumber + 2].split()[i]) for i in range(3)]
    pbc = [True if float(cell[i]) > 0.01 else False for i in range(3)]
    atoms_data = lines[2:-2]

    atoms_df = pd.read_csv(
        io.StringIO("\n".join(atoms_data)),
        sep=r"\s+",
        names=["res", "type", "id", "x", "y", "z"],
    )

    return timestep, pbc, cell, atoms_df, time


# @mprof
def get_data_gmx(pbc, cell, atoms_df, energy, atoms_forces_df, cutoff):
    typedict = {"OW": 8, "HW1": 1, "HW2": 1, "MW": -1}

    def replace_types(df, typedict):
        for key in typedict:
            df = df.replace(key, typedict[key])
        return df

    types = torch.tensor(
        # atoms_df.loc[:, "type"].replace("OW", 8).replace("HW1", 1).replace("HW2", 1).replace("MW",-1),
        # atoms_df.loc[:, "type"] repace all elements of typedict with the values of the dict
        replace_types(atoms_df.loc[:, "type"], typedict),
        dtype=torch.int32,
    )
    positions = (
        torch.tensor(atoms_df.loc[:, ["x", "y", "z"]].values, dtype=torch.float32) * 10
    )  # in nm > Angstrom
    forces = (
        torch.tensor(
            atoms_forces_df.loc[:, ["fx", "fy", "fz"]].values, dtype=torch.float32
        )
        / 41.86798
    )  # in kJ/mol/nm > kcal/mol/Angstrom
    edge_index, edge_attr = radius_graph_pbc(positions, pbc, cell, cutoff)
    ####AUSKOMMENTIERT ZUM DEBUGGEN
    # edge_index, edge_attr, angle_index, angles = radius_graph_pbc_types(positions, pbc, cell, cutoff,types) # can be used for more- eg directly all distance vectors etc
    energy = (torch.tensor(energy, dtype=torch.float32) / 4.186798).reshape(
        1, 1
    )  # kJ/mol to kcal/mol

    data = Data(
        x=forces,
        edge_index=edge_index,
        edge_attr=edge_attr,
        ###removed again- should be done by the assignment
        # angle_index=angle_index,
        # angle_values=angles,
        y=energy,
        pos=positions,
        z=types,
        # needed for disp_corr
        cell=cell,
    )
    return data


def angles(dv: torch.Tensor, dv2: torch.Tensor):
    d1 = torch.linalg.vector_norm(dv)
    d2 = torch.linalg.vector_norm(dv2)
    return float(np.rad2deg(torch.acos(torch.dot(dv, dv2) / (d1 * d2))))


# @mprof
def radius_graph_pbc_types(positions, pbc, cell, cutoff, types):
    atoms = Atoms(positions=positions, cell=cell, pbc=pbc)
    i, j, S, d, D = neighbour_list("ijSdD", atoms=atoms, cutoff=cutoff)
    # would be directly the tensors with the connection between all positions
    edge_index = torch.tensor(np.array([i, j]), dtype=torch.int64)
    a = torch.diag(torch.tensor(cell, dtype=torch.float32))
    s = torch.tensor(S, dtype=torch.float32)
    edge_attr = torch.einsum("jk,ik->ij", a, s)  # matrixmultiplikation zwischen a und s
    """
    d=torch.tensor(d)
    indices = torch.where(d < 1.3)
    connections = {}
    Dvectors={}
    i=i[indices]
    j=j[indices]
    D=D[indices]
    d=d[indices]

    for idx, val in enumerate(i):
        if val not in connections:
            connections[val] = []
            Dvectors[val]=[]
        connections[val].append(j[idx])
        Dvectors[val].append(D[idx])

    angle_index=[]
    angle_values=[]
    for key, value in connections.items():
        if len(value)==2 and types[key]==8:

            angle_index.append([key,value[0],value[1]])
            #mehr als einen winkel ausgeben?
            angle_values.append(angles(torch.tensor(Dvectors[key][0]),torch.tensor(Dvectors[key][1])))
        elif len(value)==2 and types[key]!=8:
            print("different angle types", types[key], types[value[0]],types[value[1]])
            print("anglevalue", angles(torch.tensor(Dvectors[key][0]),torch.tensor(Dvectors[key][1])))
    angle_index=torch.tensor(angle_index)
    angle_values=torch.tensor(angle_values)
    """
    return edge_index, edge_attr  # , angle_index, angle_values


# @mprof
def radius_graph_pbc(positions, pbc, cell, cutoff):
    atoms = Atoms(positions=positions, cell=cell, pbc=pbc)
    i, j, S = neighbour_list("ijS", atoms=atoms, cutoff=cutoff)
    edge_index = torch.tensor(np.array([i, j]), dtype=torch.int64)
    a = torch.diag(torch.tensor(cell, dtype=torch.float32))
    s = torch.tensor(S, dtype=torch.float32)
    edge_attr = torch.einsum("jk,ik->ij", a, s)  # matrixmultiplikation zwischen a und s
    return edge_index, edge_attr


def read_dumped_trr(filename, headerstr):
    ###liest kräfte aus output von gmx dump aus
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


# todo anderer trj reader!


def alternative_read_dumped_trj(filename, headerstr):
    ### liest positions aus output von gmx dump aus
    with open(filename, "r") as f:
        trj_sections = f.read().split(headerstr)
        trj_data = [
            parse_trj_section_gmx(trj_sections[s]) for s in range(1, len(trj_sections))
        ]
        trj_data_df = pd.DataFrame(
            trj_data, columns=["timestep", "pbc", "cell", "atoms_df", "time"]
        )
        return trj_data_df


def read_dumped_trajectory(filename, headerstr):
    print("reding trajectory")
    # liest trajektorie aus gro formati aus - falls in Zukunft nötig binär Datei xtc verwenden
    with open(filename, "r") as f:
        trajectory = f.read()

        # headerstr="SPC water for initial input of ML flexible (closer contacts?) "
        trajectory_sections = trajectory.split(headerstr)
        # print(trajectory_sections)
        # funktioniert bis hier!
        trajectory_data = [
            parse_trajectory_section_gmx(trajectory_sections[s])
            for s in range(1, len(trajectory_sections))
        ]
        trajectory_data_df = pd.DataFrame(
            trajectory_data, columns=["timestep", "pbc", "cell", "atoms_df", "time"]
        )
        # print(trajectory_data_df.head()) # worked!
        return trajectory_data_df


def parse_forces_section_gmx(section):
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


def parse_trj_section_gmx(section):
    lines = section.split("\n")
    atomnumber = int(lines[1].split()[1])
    timestep = int(lines[1].split()[3])
    time = float(lines[1].split()[4].replace("time=", ""))
    cell = [10 * float(lines[atomnumber + 2].split()[i]) for i in range(3)]
    pbc = [True if float(cell[i]) > 0.01 else False for i in range(3)]
    atoms_data = lines[7:]
    atoms_df = pd.read_csv(
        io.StringIO(
            "\n".join(atoms_data)
            .replace("f[", "")
            .replace("]", "")
            .replace("{", "")
            .replace("}", "")
            .replace(",", " ")
            .replace("=", " ")
        ),
        sep=r"\s+",
        names=["nr", "x", "y", "z"],
    )

    return timestep, pbc, cell, atoms_df, time
