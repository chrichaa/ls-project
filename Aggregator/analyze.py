def most_common(lst):
    return max(set(lst), key=lst.count)

def average(filename):
	try:
		print(filename)
		

	except IOError:
		print("An error has occured, does the file exist?")

def mostcommon(filename):
	try:
		print(filename)
		with open(filename) as f:
   			content = f.readlines()
		mostCommon=most_common(content)
		print ("Most common %s is %s", filename, mostCommon)

	except IOError:
		print("ERROR")

def main():
        print("Hello world")
        average("timestat.txt")
        mostcommon("locationstat.txt")
        mostcommon("keywordstat.txt")
        average("resultsstat.txt")

if __name__ == "__main__":
    main()
