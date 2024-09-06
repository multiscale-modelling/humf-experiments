import torch


def read_xvg_2_column(filename):
    """
    Read a xvg file with two columns and return the data as two tensors
    This is the default format of the output of gmx energy or others
    In the case of energy the first column is the time and the second the energy
    to obtain this from the edr file use gmx energy -f file.edr -o file.xvg
    """
    with open(filename, "r") as inf:
        t, e = [], []
        for line in inf:
            if "#" not in line and "@" not in line:
                t.append(float(line.split()[0]))
                e.append(float(line.split()[1]))
    return torch.tensor(t), torch.tensor(e)
