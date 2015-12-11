import json

def splitter(c):
    cities_dict={}

    for x in range(len(c)):
        temp = c[x].split("/\">")
        cities_dict[temp[0]] = temp[1].replace('</a>','').replace('<b>','').replace('</b>','').strip()
    return cities_dict

def main():
    with open("uscities.txt") as f:
        content = f.readlines()
	
    dictionary = splitter(content)
    inv_map = {v: k for k, v in dictionary.items()} 
                    
    print json.dumps(inv_map, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
