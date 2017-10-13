import sys
import os
import random
from subprocess import Popen, PIPE

def kill_bad_individual(population):	#kill worst child in population
	min_score, min_index = 99999, -1
	for i in range(len(population)):
		if population[i][-1] < min_score:
			min_score = population[i][-1]
			min_index = i
	del population[min_index]	#kill the worst!
	return 

def crossover(population):
	i = 0
	j = 0

	while i == j:
		i = random.choice(range(50))
		j = random.choice(range(50))
	try:
		parent1 = population[i]
		parent2 = population[j]
	except:
		print "parent1 i",i
		print "parent2 j",j
		print "population","\n",population
	child1 = []
	child2 = []
	for i in range(6):				
		child1.append(parent1[i])
		child2.append(parent2[i])
	for i in range(6,17):
		child1.append(parent2[i])
		child2.append(parent1[i])
	child1 = mutation(child1)
	child_score = evaluate(child1)
	child1.append(child_score)

	child2 = mutation(child2)
	child_score = evaluate(child2)
	child2.append(child_score)
	population.append(child1)
	population.append(child2)
	return 

def mutation(individual):
	i = random.choice(range(17))
	if individual[i] > 0:
		individual[i] = random.choice(range(200))	#random bit to random value
	else:
		individual[i] = -random.choice(range(200))	#random bit to random value
	for i in range(17):
		individual[i] += random.choice(range(-5,6))
	return individual

def write_to_file(population,counter):
	if counter > 0:
		fw = open("data/saved_data"+str(counter),"w")
	else:
		fw = open("data/data","w")
	for individual in population:
		for i in range(0,18):	#17 + 1 for score = 18
			fw.write(str(individual[i]))
			if i < 17:
				fw.write(' ')
			else:
				fw.write('\n')
	fw.close()

def evaluate(individual):
	score = 0
	tmp = open("data/input_data","w")
	for i in range(len(individual)):
		tmp.write(str(individual[i]))
		if i < len(individual) -1:
			tmp.write(" ")
	tmp.close()
	for j in range(1,6):	#loop thru 5 contest map
		try:
			map_name = 'contest%02dCapture' % j
			(stdout, stderr) = Popen(["python","capture.py","-r","ShuaiTeam","-q","-l",map_name], stdout=PIPE).communicate()
			if stderr:
				print stderr
				sys.exit()
			result = stdout.split("\n")[-2]
			if "wins" in result:
				if "Blue" in result:
					score -= int(result.split(" ")[5])
				elif "Red" in result:
					score += int(result.split(" ")[5])
			elif 'returned' in result:
				if "Blue" in result:
					score -= 28
				elif "Red" in result:
					score += 28
		except:
			print "Fail on map Contest%ddefaultCapture" % j
	return score

if __name__ == '__main__':
	TestOn = True
	for i in range(1,len(sys.argv)):
		if sys.argv[i]=='-h':
			print '''
			-g real go!, no more testing
			'''
			sys.exit()
		elif sys.argv[i] == '-g':
			TestOn = False
		else:
			print "Invalid option!!",i
			sys.exit()
	
	fr = open("data/data","r")
	data = fr.read().split("\n")
	data.remove("")
	#print data
	population = []
	for i in data:
		individual = [int(j) for j in i.split(" ")]
		population.append(individual)
	fr.close()

	counter = 9
	for i in range(2000):	#train generation count here~
		print "generation",i
		crossover(population)	
		kill_bad_individual(population)	#kill two to maintain the individual number in population
		kill_bad_individual(population)
		if not TestOn and i % 200 == 0:
			write_to_file(population,counter)
			counter+=1
		elif i % 10 == 0:
			write_to_file(population,-1)

	if TestOn:
		print "Test Over\n"
