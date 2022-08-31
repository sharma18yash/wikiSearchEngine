import filehandling
import os
index_count = 5
print("MERGING FILES")
fh = filehandling.file_handling(index_count)
secondary_index_files = fh.merge()
print("SECONDARY FILES CREATED: ", secondary_index_files )

# print("REMVOVING TEMPORARY FILES")

# for i in range(0, index_count):
#     os.remove("tmp/index{}.txt".format(i))