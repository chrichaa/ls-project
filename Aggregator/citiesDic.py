def splitter(c):
	cities_dict={}
	for x in range(len(c))
		temp=c[x].split("/\">")
		cities_dict[temp[0]=temp[1]
	return cities_dict

def main():
	#print("hello world")
	with open("uscities.txt") as f:
		content=f.readlines()
	dictionary=splitter(content)
if __name__ == "__main__":
    main()
