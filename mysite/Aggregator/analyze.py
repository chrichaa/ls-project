def avg(l):
	s=0
	for s in range(0, len(l)):
		l[s]=float(l[s])
	try:
    		return sum(l, 0.0) / len(l)
	except ZeroDivisionError:
		print("List is empty!")

def most_common(lst):
	return max(set(lst), key=lst.count)

def average(filename):
	try:
		#print(filename)
		with open(filename) as f:
			content=f.readlines()
		average=avg(content)
		
		print("The average "+filename[:-4]+" is "+str(average))
	except(IOError):
		print("An error has occured, does the file "+filename+" exist?")

def mostcommon(filename):
	try:
		#print(filename)
		with open(filename) as f:
   			content = f.readlines()
		mostCommon=most_common(content)
		print ("Most common "+filename[:-4]+" is "+mostCommon[:-1])

	except IOError:
		print("ERROR, does the file exist?")

def main():
       # print("Hello world")
        average("timestat.txt")
        mostcommon("locationstat.txt")
        mostcommon("keywordstat.txt")
        average("resultsstat.txt")

if __name__ == "__main__":
    main()
