from cmath import log10
import time
import math
import json
import sys
import preprocess
from nltk.stem import PorterStemmer

queries= sys.argv[1]

output_file = sys.argv[2]
pre = preprocess.Preprocess()
ps = PorterStemmer()

word_file = {}
for i in range(0, 9):
    word_file[str(i)] = "tmp/final_index{}.txt".format(i)

c = 97
for i in range(10, 35):
    word_file[chr(c)] = "tmp/final_index{}.txt".format(i)
    c+=1
word_file['9'] = "tmp/misc.txt"
word_file['z'] = "tmp/misc.txt"
word_file['@'] = "tmp/final_index9.txt"
# all_titles = []


# with open('final/title_list.txt') as f:
#   all_titles = json.load(f)

number_of_title_files = 223
title_files = []
for i in range(0, number_of_title_files):
    title_files.append(i)

category_index = { "b":0, "i":1, "c":2, "r":3, "t":4,  "e":5}

section_weights = {0:20, 1:60, 2:50, 3:40, 4:100, 5:30}
    
stopwords = pre.getStopWords()


def read_file(file_name):
    temp = {}
    with open(file_name) as fp:
        Lines = fp.readlines()
        for line in Lines:
            line = line.strip("\n")
            data = line.split("~")
            try:
                temp[data[0]] = data[1]
            except IndexError:
                pass
    return temp

def get_posting_list(query):
    posting_lists= {}
    for word in query.split():
        try:
            file_name = word_file[word[0]]
            
        except KeyError:
            file_name = "misc.txt"
        # print(file_name)
        # print(file_name, word, word[0])
        all_words = read_file(file_name)
        try:
            posting_lists[word] = all_words[word]
        except KeyError:
            print(word, "NOT FOUND")
    # print(posting_lists)
    del all_words
    return posting_lists



def page_rank(all_docs, extracted_info):
    tf_idf = {}
    N = 22200000
    for data in extracted_info:
        document_frequency = len(data)
        term_frequency = sum(data[1:7])
        score = term_frequency * math.log10(N/document_frequency)
        if data[0] in tf_idf.keys():
            tf_idf[data[0]] += score
        else:
            tf_idf[data[0]] = score
    # print(tf_idf)
    ranks = sorted(tf_idf.items(), key = lambda x: x[1], reverse = True) 
    docs = []
    for key, value in ranks:
        docs.append(key)
    del ranks
    return docs

def process_posting_list(posting_lists, count=10, special = False):
    extracted_info = []
    all_docs = []
    for key in posting_lists.keys():
        data = posting_lists[key]
        data = data.split("|")
        docs = []
        
        for word in data:
            word = word.split("-")
            current_data = [0]*8
            for token in word:
                if len(token) == 0:
                    continue
                if token[0] == 'd':
                    current_data[0] = int(token[1:])
                if token[0] == 'b':
                    current_data[1] = int(token[1:])*section_weights[category_index["b"]]
                if token[0] == 'i':
                    current_data[2] = int(token[1:])*section_weights[category_index["i"]]
                if token[0] == 'c':
                    current_data[3] = int(token[1:])*section_weights[category_index["c"]]
                if token[0] == 'r':
                    current_data[4] = int(token[1:])*section_weights[category_index["r"]]
                if token[0] == 't':
                    current_data[5] = int(token[1:])*section_weights[category_index["t"]]
                if token[0] == 'e':
                    current_data[6] = int(token[1:])*section_weights[category_index["e"]]
            current_data[7] = key
            docs.append(current_data[0])
            extracted_info.append(current_data)
        all_docs.append(docs)
    
    page_ranks = page_rank(all_docs, extracted_info)

    # for i in page_ranks:
    #     for j in extracted_info:
    #         if j[0] == i:
    #             print(j)
    del all_docs
    k = min(len(page_ranks), count)
    titles = []
    for i in range(len(page_ranks)):
        titles.append(page_ranks[i])

    if(special):
        return titles, extracted_info
    return titles

def writetofile(ans):
    with open(output_file, 'a') as f:
        for i in ans:
            f.write(i)
            f.write("\n")
        f.write("\n")
    
def get_title(title):
    ind = title
    title_file_ind = ind//100000
    # print(ind, title_file_ind)
    value = title_files[title_file_ind]
    all_titles = []
    # if(value == "B"):
    #     with open("tmp/title_list.txt") as f:
    #         all_titles = json.load(f)
    # else:
    with open("tmp/title_list{}.txt".format(value)) as f:
        while True:
            data = f.readline().strip("\n")
            if(len(data) == 0):
                break
            else:
                all_titles.append(data)
        

    title_ind = ind - 100000*title_file_ind
    print(value, title_ind, len(all_titles))
    # print(all_titles[title_ind],", ", all_titles[title_ind+1],", ", all_titles[title_ind+2])
    # print(title_ind, title_file_ind, len(all_titles))
    return all_titles[title_ind]

def process_special_query(query):
    query = query.split()
    word_cat = {}
    new_query = []
    
    cat = "1"
    for word in query:
        if "i:" in word or "b:" in word or "c:" in word or "r:" in word or "e:" in word or "t:" in word:
            cat = word[0:1]
            tok = word[2:]
            tok = ps.stem(tok)
            if tok in stopwords:
                continue
            word_cat[tok] = cat
            new_query.append(tok)
        else:
            tok = ps.stem(word)
            if tok in stopwords:
                continue
            word_cat[tok] = cat
            new_query.append(tok)

    
    
    new_query = " ".join(new_query)
    new_query = pre.remove_stopwords(new_query)
    new_query = pre.stemmer(new_query)
    # print(word_cat, new_query)
    posting_lists = get_posting_list(new_query)
    titles, extracted_info = process_posting_list(posting_lists, count=10, special=True)
    
    del posting_lists

    title_category = {}
    for arr in extracted_info:
        title_category[arr[0]] = arr[1:]

    count = 0
    # print(titles)
    # print(extracted_info[:10])
    # print()
    ans = []
    for title in titles:
        categories = title_category[title]
        # print(categories)
        word = categories[6]
        word_c = word_cat[word]
        ind = category_index[word_c]
        if categories[ind] > 0:
            curr_title = get_title(title-1)
            ans.append(curr_title)
            count+=1
            if count == 10:
                break
    del titles, extracted_info
    writetofile(ans)
    

            


t1 = time.time()

with open(queries, 'r') as f:
    
    while(True):
        query = f.readline().strip("\n")
        if len(query) == 0:
            break
        query = query.lower()
        if "i:" in query or "b:" in query or "c:" in query or "r:" in query or "e:" in query or "t:" in query:
            # print(query)
            output = process_special_query(query)
        else:
            new_query = pre.remove_stopwords(query)
            new_query = pre.stemmer(new_query)
            posting_lists = get_posting_list(new_query)
            output = process_posting_list(posting_lists, 10)

            count = 0
            ans = []
            for title in output:
                curr_title = get_title(title-1)
                ans.append(curr_title)
                count+=1
                if count == 10:
                    break
            writetofile(ans)

t2 = time.time()
    # print(posting_lists)
print("TIME TAKEN: ", t2-t1)
    


    