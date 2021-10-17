import pandas as pd
import csv

# foo_lst = [Note,Trumpet,Trombone,Euphonium,Tuba,French Horn]

notes_dict = {}

with open('testing/FingeringTable.csv','r') as csvfile:
    lines = csvfile.readlines()
    for row in lines:
        row = row.strip().split(",")

        for count, elem in enumerate(row):
            if elem == '':
                row[count] = "NaN"

        note = row[0]
        trumpet = row[1]
        trombone = row[2]
        euphonium = row[3]
        tuba = row[4]
        french_horn = row[5]

        current_note_dict = {
                "trumpet": trumpet, 
                "trumbone": trombone,
                "euphonium": euphonium,
                "tuba": tuba,
                "french horn": french_horn
            }
        notes_dict[note] = current_note_dict

print(notes_dict)
