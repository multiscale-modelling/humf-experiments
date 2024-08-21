with open("reduced_times.gro","w") as of:

	with open("reduced.gro","r") as inf:
		dt=5
		counter=0
		for line in inf:
			if "t=" in line:
				line=line.replace(line.split(sep="=")[1].split()[0], "{:.5f}".format(float(round(dt*counter,5)) ))
				print(line, end="", file=of)
				counter+=1
			else:
				print(line, end="", file=of)
