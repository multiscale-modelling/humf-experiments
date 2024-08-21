set -e

# See: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

datafolder=$1
M_Molecules=$2
concatenate=$3

echo "assuming 3 point water model"
echo "assuming the data is under $datafolder as nvt.xtc, nvt.gro and an additional system_sed.top with REPLACE instead of the original molecule number"
echo "assuming increasing_indices.py and fix_times.py is in the current (output) folder"
echo "if 4 pt change indices generating script to increasing_indices_4pt.py and atnr multiplicative factor to 4"

echo "concatenating $M_Molecules Molecules $concatenate times"

python3 "$SCRIPT_DIR/increasing_indices.py" --N_concat ${concatenate} --M_molecules ${M_Molecules}
for ((i = 0; i < ${concatenate}; i++)); do
	echo $i
	cat ${i}_tmp.ndx
	echo "r_1 System" | gmx trjorder -f ${datafolder}/nvt.xtc -s ${datafolder}/nvt.tpr -n ${datafolder}/sort.ndx
	gmx trjconv -f ordered.xtc -s ${datafolder}/nvt.gro -o reduced_${i}.xtc -n ${i}_tmp.ndx
done
gmx trjcat -f reduced_*.xtc -o reduced.xtc -cat
read -p "new tpr needed"
sed "s|REPLACE|${M_Molecules}|g" ${datafolder}/system_sed.top >current_system.top

#needs a new variable gro file for M_molecules
head -n 1 ${datafolder}/nvt.gro >tmp.gro
atnr=$(python3 -c "print($M_Molecules * 3)")
echo $atnr
echo $atnr >>tmp.gro
head -n $((2 + $atnr)) ${datafolder}/nvt.gro | tail -n $atnr >>tmp.gro
tail -n 1 ${datafolder}/nvt.gro >>tmp.gro
cat tmp.gro
read -p "check tmp.gro"
gmx grompp -f ${datafolder}/nvt_f.mdp -o rename_tpr.tpr -c tmp.gro -p current_system.top
read -p "tpr done"
rm tmp.gro
echo -ee "r1 \n q \n" | gmx make_ndx -f rename_tpr.tpr -o cluster.ndx
echo "0 3 0" | gmx trjconv -f reduced.xtc -o reduced.gro -s rename_tpr.tpr -pbc cluster -center -n cluster.ndx
read -p "trjconv correct???"
python3 "$SCRIPT_DIR/fix_times.py"
ls reduced_*.xtc | xargs rm
ls *tmp.ndx | xargs rm
rm reduced.xtc
mv reduced_times.gro reduced.gro

gmx grompp -f ${datafolder}/nvt_rerun.mdp -c reduced.gro -o tmp -p current_system.top
gmx mdrun -deffnm tmp -rerun reduced.gro
echo "Potential" | gmx energy -f tmp.edr
gmx dump -f tmp.trr >dumped_forces.txt
