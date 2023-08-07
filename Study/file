# Open a txt file in the same dir and sent the data to a file called output
#It will also close the file
with open("filename.txt") as file:
  output = file.read()  #Options - .readline() - .readlines()
# read will read file - readline will read one line - readlines will read the file and return each line as a list

#Write to a file
with open("filename.txt", "w") as file:  #"a" if you want to append
  file.write("something")


#Read a csv file
import csv

with open("filename.csv", "r", encoding="utf-8") as file:
    output = csv.reader(file)
    for row in output:
        print(row)

#If you want to retrive the reader use - next(file)

#Writing to csv file

import csv
header = ["name", "surname"]
name_surname = "wellington", "oliveira"
with open("test.csv", "w", newline="") as file:
    write = csv.writer(file)
    write.writerow(header)
    write.writerow(name_surname)
