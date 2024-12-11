import csv

devices = []
my_set = set()
with open("input_life.csv", "r") as file:
    output = csv.reader(file)
    for row in output:
        my_set.add(tuple(row))

for obj in my_set:
    devices.append(list(obj))
    
with open("output_file.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(devices)
