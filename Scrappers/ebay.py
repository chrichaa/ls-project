import ebaysdk
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError

def main():
    try:
        api = Finding(appid="Jeremiah-c9e4-41cd-93a3-db5086f58faf")
        response = api.execute('findItemsAdvanced', {'keywords': '3930k'})
        print(response.dict())
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

main()