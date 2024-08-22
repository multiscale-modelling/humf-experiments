import argparse

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument(
    "--M_molecules", type=int, help="an integer for the number of molecules"
)
parser.add_argument(
    "--N_concat", type=int, help="an integer for the number of concatenations"
)
args = parser.parse_args()

M_molecules = args.M_molecules
N_concat = args.N_concat


def print_indices(K, M):
    # prints indices for K molecules (per frame) and does this up to M times
    K = 3 * (K - 1)

    for i in range(M):
        filename = str(i) + "_tmp.ndx"
        with open(filename, "w") as of:
            print("[ M ]", file=of)
            print(1, 2, 3, end=" ", file=of)

            for j in range(1, K + 1):
                print(3 + i * K + j, end=" ", file=of)


print_indices(M_molecules, N_concat)
