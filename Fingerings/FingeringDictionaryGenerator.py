import csv

def readFingeringDataset():
    with open('FingeringTable.csv', mode='r') as input:
        reader = csv.reader(input)
        TrumpetDict = {rows[0]:rows[1] for rows in reader}
        input.seek(0)
        TromboneDict = {rows[0]:rows[2] for rows in reader}
        input.seek(0)
        EuphoniumDict = {rows[0]:rows[3] for rows in reader}
        input.seek(0)
        TubaDict = {rows[0]:rows[4] for rows in reader}
        input.seek(0)
        FrenchHornDict = {rows[0]:rows[5] for rows in reader}

    DictionaryList = [TrumpetDict, TromboneDict, EuphoniumDict, TubaDict, FrenchHornDict]
    for dict in DictionaryList:
        del dict['\xef\xbb\xbf']
    return DictionaryList

def run():
    readFingeringDataset()

if __name__ == "__main__":
    run()
