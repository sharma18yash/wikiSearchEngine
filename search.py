word_file = {}
for i in range(0, 9):
    word_file[str(i)] = "final_index{}.txt".format(i)

c = 97
for i in range(10, 35):
    word_file[chr(c)] = "final_index{}.txt".format(i)
    c+=1
word_file['9'] = "misc.txt"
word_file['z'] = "misc.txt"
print(word_file)
    