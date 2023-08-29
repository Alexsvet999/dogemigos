import csv
from dogemigos import ROOT_PATH
from w3f.lib.logger import to_json_str

CSV_PATH = ROOT_PATH / "dat/other/WL.csv"
JSON_PATH = ROOT_PATH / "dat/other/WL.json"
TXT_PATH = ROOT_PATH / "dat/other/WL.txt"

def to_dict():
    whitelist = {}
    with open(CSV_PATH, encoding="utf8") as f:
        reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        for row in reader:
            whitelist.setdefault(row[0], []).extend(row[1:])

        print(to_json_str(whitelist))
    return whitelist

flatlist = set()
def flatten(whitelist: dict):
    with open(TXT_PATH, 'w') as f:
        for hodler in whitelist:
            if len(whitelist[hodler]) > 5:
                raise RuntimeError(f"Too many wallets: {hodler}: {whitelist[hodler]}")
            for address in whitelist[hodler]:
                flatlist.add(address)

        for address in flatlist:
            print(address)
            f.write(f"{address}\n")

        flatlist.add("0x05b48a6d0c5c521b5417641759cfc0de661d5d06")


def main():
    flatten(to_dict())

if __name__ == "__main__":
    main()