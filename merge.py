import filehandling
import os
import sys
import time
index_count = sys.argv[1]
index_count = int(index_count)
t1 = time.time()
print("MERGING FILES")
fh = filehandling.file_handling(index_count)
secondary_index_files = fh.merge()
t2 = time.time()
print("SECONDARY FILES CREATED: ", secondary_index_files )
print("TIME TAKEN TO COMPLETE SECONDARY INDEXING: ", t2-t1)

print("REMVOVING TEMPORARY FILES")

for i in range(0, index_count):
    os.remove("tmp/index{}.txt".format(i))