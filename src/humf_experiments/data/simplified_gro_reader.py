"""
This is simplified_gro_reader.py. This module does exactly what is named after...
"""
import numpy as np
import io
from contextlib import contextmanager
from ase import Atoms, Atom
import multiprocessing

@contextmanager # for things that are used in a "with" environment!
def smart_open(file, mode):
	if isinstance(file, io.StringIO):
		file.seek(0)
		yield file
	else:
		with open(file, mode) as f:
			yield f

def extract_bonds(dump_from_itp):
	reading_bonds=False
	bonds=[]
	for entry in dump_from_itp:
		if "[ bonds ]" in entry:
			reading_bonds=True
		elif "[ angles ]" in entry:
			reading_bonds=False
		elif reading_bonds is True:
			if len(entry.split()) >1:
				bonds.append(entry.split()[:2])
	return  np.array(bonds, dtype=int)


def get_num_frames(gro_file):
	with smart_open(gro_file, "r") as inf:
		commentline=None
		counter=0
		for line in inf:
			if commentline is None:
				commentline=line.split(sep="t=")[0]
				counter+=1
			elif commentline in line:
				counter+=1
			else:
				pass
	return counter, commentline

def split_trj_gro(gro_file,splitstring, selected_frames):
	temp_file=io.StringIO()
	with smart_open(gro_file, "r") as inf:
		all_frames=inf.read().split(sep=splitstring)
	for frame in all_frames[selected_frames]:
		temp_file.write(frame)

	temp_file.seek(0)
	return temp_file


def extract_coordinates_all(file):
	counter=0
	forces_present=False
	x_dump, y_dump, z_dump=[],[],[]
	fx_dump, fy_dump, fz_dump=[],[],[]
	symbols=[]
	BOX=-1
	
	with smart_open(file,"r") as inf:
		for line in inf:
			#print(line)
			if counter==0:
				counter+=1
			elif counter==1:
				counter+=1
			elif len(line.split())==3:
				#print(line)
				BOX=(float(line.split()[0]))
			else:
				#xyz is badly defined in this manner for  a gro file if more than 1000 atoms are present
				#instead use the character positions
				#check whether forces are present
				if len(line.split())>6:
					forces_present=True
					fx=float(line[44:52])
					fy=float(line[52:60])
					fz=float(line[60:68])
					fx_dump.append(fx)
					fz_dump.append(fz)
					fy_dump.append(fy)
				x=float(line[20:28])
				y=float(line[28:36])
				z=float(line[36:44])
				current_symbol=line[12:15].strip()
				
				x_dump.append(x)
				z_dump.append(z)
				y_dump.append(y)
				symbols.append(current_symbol)
	if not forces_present:			
		return (np.array([np.array(x_dump, dtype=float), np.array(y_dump, dtype=float), np.array(z_dump,dtype=float)]),None, BOX, symbols)
	else:
		return (np.array([np.array(x_dump, dtype=float), np.array(y_dump, dtype=float), np.array(z_dump,dtype=float)]), [np.array(fx_dump, dtype=float), np.array(fy_dump, dtype=float), np.array(fz_dump,dtype=float)], BOX, symbols)



def rm_comments(itpfile):
	dump=[]
	with smart_open(itpfile, "r") as inf:
		for line in inf:
			if ";" in line:
				line=line.split(";")[0]
				if len(line)> 0:
					dump.append(line)
			else:
				dump.append(line)
#			print(line)
	return dump
	
 

def extract_charges(dump):
	reading_charges=False
	charges=[]
	for entry in dump:
		if "[ atoms ]" in entry:
			reading_charges=True
		elif "[ bonds ]" in entry:
			reading_charges=False
		elif reading_charges is True:
			charges.append(float(entry.split()[6]))
	return np.array(charges) 


def to_ase_atoms(coords,symbol, box,forces, charges):
	print("guessing atom - if you have Elements with multiple letters or atomnames not starting with the chemical symbol please correct it afterwards")
	using_forces=False
	using_charges=False
	symbols_guessed=[c[0] for c in symbol]
	mycell=np.array([[box,0,0],[0,box,0],[0,0,box]])

	coords=coords.T
	#check whether forces are present
	if forces is not None:
		forces=forces.T
		using_forces=True
	#check whether charges are present
	if charges is not None:
		using_charges=True
	#create an ase atoms object from the coordinates with the correct symbols
	#and the box
	if not using_charges:
		a=Atoms([Atom(symbol=s, position=p) for s,p in zip(symbols_guessed, coords)], cell=mycell, pbc=True)
		#write all symbols and forces into the info part of the atoms object
		if using_forces:
			a.info["forces_total"]=forces
			a.info["atomtypes"]=symbol
		else:
			a.info["forces_total"]=None
			a.info["atomtypes"]=symbol
	else:
		a=Atoms([Atom(symbol=s, position=p, charge=c) for s,p,c in zip(symbols_guessed, coords, charges)], cell=mycell, pbc=True)	
		#write all symbols and forces into the info part of the atoms object
		if using_forces:
			a.info["forces_total"]=forces
			a.info["atomtypes"]=symbol
		else:
			a.info["forces_total"]=None
			a.info["atomtypes"]=symbol
	return a


def extract_coordinates_parallel(args):
			grofile, splitstring, frame, charges = args
			coords, forces, box, symbol = extract_coordinates_all(split_trj_gro(grofile, splitstring, frame))
			return to_ase_atoms(coords, symbol, box, forces, charges)


def extract_all_coordinates_from_gro_file(grofile:str,itpfile:str|None, processes:int=3):
	results_list=[]
	'''
	Extracts all coordinates from a gro file and returns them as a list of ase Atoms objects
	itpfile is the topology corrspoding to the grofile but it is assumed that only 1 kind of molecule is present
	
	'''
	maxframes,splitstring=get_num_frames(grofile)
	if itpfile is not None:
		charges=extract_charges(rm_comments(itpfile))
	else:
		charges=None

	pool = multiprocessing.Pool(processes=processes)
	results = pool.map(extract_coordinates_parallel, [(grofile, splitstring, frame, charges) for frame in range(1,maxframes)])
	pool.close()
	pool.join()

	results_list = results

	return results_list

#test feature
'''
res=extract_all_coordinates_from_gro_file("/home/dullinger/cos_theta/test.gro", "/home/dullinger/cos_theta/jrd1_modified.itp")

print(res)
input("press enter")
print(res[0])
input("press enter")
print(res[0].info)
print(res[0].info["forces_total"])
input("press enter")
print(res[0].info["atomtypes"])
input("press enter")
print(res[0].cell)
input("press enter")
print(res[0].positions)


'''