import csv

engine_db = {}
with open('engines.csv', newline='') as f:
    csv_reader = csv.reader(f, delimiter=',')
    line = 0
    for row in csv_reader:
        if line != 0 and row[0] != '':
            engine_db[row[0]] = {
                'thrust': float(row[1]),
                'weight': float(row[2]),
                'cj': float(row[3]),
                'cost': int(row[4]),
            }
        line += 1