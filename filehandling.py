from collections import defaultdict
from curses.ascii import isalpha
import json
from xml.dom.minidom import Element
import heap

from collections import Counter


file_pointer = []
for i in range(0, 5):
    file_pointer.append(open("tmp/index{}.txt".format(i)))

result = defaultdict(list)
 

l = []
hp = heap.MinHeap()
final_dict = {}
for p in file_pointer:
    data = p.readline()
    data = data.split(":")
    if(len(data) > 2):
        print("error occured at: ", data)
    key = data[0]
    value = data[1]
    hp.insert([key,p, value])

hp.minheap()

final_dict = {}
index_count = 0
error_count = 0
unique_tokens = 0
prev = '0'
while(hp.size > 0):
    try:
        key, fp, value = hp.remove()
    except ValueError:
        value = ""
    value = value.strip("\n")

    if key in final_dict.keys():
        final_dict[key] += value
    else:
        final_dict[key] = value

    data = fp.readline().strip("\n")
    if len(data) > 0:
        data = data.split(":")
        if(len(data) > 2):
            error_count+=1
        key = data[0]
        value = data[1]
        hp.insert([key, fp, value])

        if key[0] != prev:
            if key[0].isalpha or key[0].isnum: 
                with open('final/final_index{}.txt'.format(index_count), 'w') as f: 
                    for key, value in final_dict.items(): 
                        f.write('%s:%s\n'% (key, value))
                index_count+=1
            else:
                with open('final/misc.txt'.format(index_count), 'a') as f: 
                    for key, value in final_dict.items(): 
                        f.write('%s:%s\n'% (key, value))
            
            unique_tokens += len(final_dict)
            final_dict = {}
            prev = key[0]

with open('final/final_index{}.txt'.format(index_count), 'w') as f: 
    for key, value in final_dict.items(): 
        f.write('%s:%s\n'% (key, value))
    unique_tokens+= len(final_dict)
    final_dict = {}


print("Unique tokens count: ", unique_tokens)
print("error_count: ", error_count)