from collections import defaultdict
from curses.ascii import isalpha
import json
from xml.dom.minidom import Element
import heap

from collections import Counter

class file_handling:
    def __init__(self, file_count) -> None:
        self.file_count = file_count
        self.file_pointer = []
        for i in range(0, file_count):
            self.file_pointer.append(open("tmp/index{}.txt".format(i)))

    
    def merge(self):
        l = []
        hp = heap.MinHeap()
        final_dict = {}
        error_count = 0
        for p in self.file_pointer:
            data = p.readline()
            data = data.split(":")
            if(len(data) != 2):
                print("error occured at: ", data)
            else:
                key = data[0]
                value = data[1]
                hp.insert([key,p, value])

        hp.minheap()

        final_dict = {}
        index_count = 0
        unique_tokens = 0
        prev = '0'
        while(hp.size > 0):
            try:
                key, fp, value = hp.remove()
            except ValueError:
                value = ""
            value = value.strip("\n")

            if len(key) > 0:
                if key[0] != prev:
                    # print(key[0], prev)
                    prev = key[0]
                    if ( ord(key[0]) >= 97 and ord(key[0]) <= 122) or ( ord(key[0]) >= 48 and ord(key[0]) <= 57):
                        # print("printing key[0]: ", key[0])
                        with open('final/final_index{}.txt'.format(index_count), 'a') as f: 
                            for key, value in final_dict.items():
                                # if(key[0] == 'z'):
                                    # print(key, index_count) 
                                f.write('%s~%s\n'% (key, value))
                        index_count+=1
                        unique_tokens += len(final_dict)
                        final_dict = {}
                    else:
                        # print("misc :",  key[0])
                        with open('final/misc.txt', 'a') as f: 
                            for key, value in final_dict.items(): 
                                f.write('%s~%s\n'% (key, value))
                        unique_tokens += len(final_dict)
                        final_dict = {}
            


            if key in final_dict.keys():
                final_dict[key] += value
            else:
                final_dict[key] = value

            data = fp.readline().strip("\n")
            if len(data) > 0:
                data = data.split(":")
                if(len(data) != 2):
                    error_count+=1
                else:
                    key = data[0]
                    value = data[1]
                    hp.insert([key, fp, value])

        with open('final/misc.txt', 'a') as f: 
            # print("printing prev: ", prev)
            for key, value in final_dict.items(): 
                f.write('%s~%s\n'% (key, value))
            unique_tokens+= len(final_dict)
            final_dict = {}


        print("Unique tokens count: ", unique_tokens)
        print("error_count: ", error_count)

        return index_count+1