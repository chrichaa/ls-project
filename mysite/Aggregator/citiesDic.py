import json
from collections import OrderedDict

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
    dic = {v: k for k, v in dictionary.items()}
                    
    tmp = json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    for key,value in sorted(dic.items()):
       print "('" + key + "' , '" + value + "'),"

if __name__ == "__main__":
    main()
