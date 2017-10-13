import random

f = open("data/data","w")

pos_neg = [1,1,0,0,0,0,0,1,0,1,1,1,0,1,1,0,1,0]

for i in range(50):
	for j in range(17):
		tmp = random.choice(range(1,200))
		if pos_neg[j] == 1:
			f.write(str(tmp))
			if j <= 15:
				f.write(' ')
			else:
				f.write("\n")
		else:
			f.write(str(-tmp))
			if j <=15:
				f.write(' ')
			else:
				f.write("\n")
