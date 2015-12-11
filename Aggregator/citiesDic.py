import json

def splitter(c):
    cities_dict={}

    for x in range(len(c)):
        temp = c[x].split("/\">")
        cities_dict[temp[0]] = temp[1]
    return cities_dict

def main():
    with open("uscities.txt") as f:
        content = f.readlines()
	
    dictionary = splitter(content)
                    
    print json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
