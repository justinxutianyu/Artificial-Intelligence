
for i in range(12):
	file = 'saved_data'
	f = open(file+str(i),'r')
	lines = f.read().split("\n")
	lines.remove('')
	max = -1000
	for line in lines:
		if int(line.split(" ")[-1]) > max:
			max = int(line.split(" ")[-1])
	
	print max, 