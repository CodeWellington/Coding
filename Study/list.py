#!/usr/bin/python3
#Methods for list
"""
.append()
.extend()
.insert(index,value)
.pop()
Del listname[index]
.remove(value)
.count(argument)
.index(argument)
"argument".join()
"""

#A common Python technique is to use range(len(someList)) with a for loop to iterate over the indexes of a list.
# For example:

supplies = ['pens', 'staplers', 'flame-throwers', 'binders']
for i in range(len(supplies)):
    print('Index ' + str(i) + ' in supplies is: ' + supplies[i])

