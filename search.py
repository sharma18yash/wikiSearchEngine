from cmath import log10
import time
import math
import json
import sys
from unittest import result
from xxlimited import new
import preprocess
from nltk.stem import PorterStemmer
t1 = time.time()


number_of_title_files = 223




queries= sys.argv[1]

output_file = sys.argv[2]
pre = preprocess.Preprocess()
ps = PorterStemmer()

# def term_frequency_penalty():
#     term_frequency_penalty = {}
#     with open("document_frequency.txt", 'r') as f:
#         while(True):
#             line = f.readline()
#             line = line.strip("\n")
#             if len(line) == 0:
#                 break
#             data = line.split("~")
#             term_frequency_penalty[data[0]] = data[1]
#     return term_frequency_penalty

def load_secondary_index():
    secondary_index = []
    with open("tmp/secondary_index.txt", 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            temp = []
            line = line.strip("\n")
            data = line.split("~")
            temp.append(data[0])
            temp.append(data[1])
            secondary_index.append(temp)
    return secondary_index

secondary_index = load_secondary_index()
# term_frequency_pen = term_frequency_penalty()

def binary_search(word):
    low = 0
    high = len(secondary_index)-1
    while(low <= high):
        mid = (low + high)//2
        if(word >= secondary_index[mid][0] and word <= secondary_index[mid][1]):
            return mid
        if word > secondary_index[mid][1]:
            low = mid+1;
        else:
            high = mid-1;
    return "xx"

title_files = []
for i in range(0, number_of_title_files):
    title_files.append(i)

category_index = { "b":0, "i":1, "c":2, "r":3, "t":4,  "e":5}

section_weights = {0:10, 1:50, 2:30, 3:30, 4:100, 5:20}
    
stopwords = pre.getStopWords()


def read_file(file_name, word):
    temp = {}
    with open(file_name) as fp:
        Lines = fp.readlines()
        for line in Lines:
            line = line.strip("\n")
            data = line.split("~")
            # try:
            #     temp[data[0]] = data[1]
            # except IndexError:
            #     pass
            if data[0] == word:
                temp[data[0]] = data[1]
    return temp

def get_posting_list(query):
    posting_lists= {}
    for word in query.split():
        
        index = binary_search(word)
        if(index == "xx"):
            print(word, "NOT FOUND")
        else:
            file_name = "tmp/final_index{}.txt".format(index)
        # print(file_name)
        # print(file_name, word)
        all_words = read_file(file_name, word)
        try:
            posting_lists[word] = all_words[word]
        except KeyError:
            print(word, "NOT FOUND")
    # print(posting_lists)
    del all_words
    return posting_lists


def intersect(d):
    res = set.intersection(*map(set,d))
    return res

def page_rank(all_docs, extracted_info):
    tf_idf = {}
    N = 22200000
    for data in extracted_info:
        document_freq = data[8]
        term_frequency = sum(data[1:7])
        score = (term_frequency) * math.log10(N/document_freq)
        if data[0] in tf_idf.keys():
            tf_idf[data[0]] += score
        else:
            tf_idf[data[0]] = score
    ranks = sorted(tf_idf.items(), key = lambda x: x[1], reverse = True) 
    docs = []
    for key, value in ranks:
        docs.append(key)
    del ranks
    return docs

def merge_posting_list(posting_lists):
    title_posting_dict = []
    all_titles_ind = []
    key_list = []
    for key in posting_lists.keys():
        key_list.append(key)
        posting_list = posting_lists[key]
        all_docs = posting_list.split("|")
        d = {}
        title_ind = set()
        for val in all_docs:
            arr = val.split("-")
            try:
                d[int(arr[0][1:])] = val
                title_ind.add(int(arr[0][1:]))
            except:
                pass
        title_posting_dict.append(d)
        all_titles_ind.append(title_ind)
    l=0
    for arr in all_titles_ind:
        l+=len(arr)
    # print("all titles: ", l)
    all_titles_ind =  intersect(all_titles_ind)
    # print("Afetr intersection: ", len(all_titles_ind))
    all_titles_ind = list(all_titles_ind)
    # print(all_titles_ind)
    # print(all_titles_ind)
    new_posting_lists = {}
    for title in all_titles_ind:
        ind = 0
        for key in key_list:
            if key in new_posting_lists:
                new_posting_lists[key] += title_posting_dict[ind][title] + "|"
            else:
                # print(ind, title)
                # print("printing this: ", title_posting_dict[ind][title])
                new_posting_lists[key] = title_posting_dict[ind][title] + "|"
            ind+=1
    
    with open("temp1.txt", 'w') as f:
        for key in new_posting_lists.keys():
            f.write("%s~%s\n"%(key, new_posting_lists[key]))

    return new_posting_lists


def process_posting_list(posting_lists, documet_frequency,  count=10, special = False):
    extracted_info = []
    all_docs = []
    for key in posting_lists.keys():
        data = posting_lists[key]
        data = data.split("|")
        docs = []
        
        for word in data:
            word = word.split("-")
            current_data = [0]*9
            for token in word:
                try:
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
                except ValueError:
                    pass
            current_data[7] = key
            current_data[8] = documet_frequency[key]
            docs.append(current_data[0])
            extracted_info.append(current_data)
        all_docs.append(docs)
    
    page_ranks = page_rank(all_docs, extracted_info)
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
    # print(value, title_ind, len(all_titles))
    # print(all_titles[title_ind],", ", all_titles[title_ind+1],", ", all_titles[title_ind+2])
    # print(title_ind, title_file_ind, len(all_titles))
    return all_titles[title_ind]

def process_special_query(query):
    # print("in special query ")
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
    docuement_frequency = {}
    for key in posting_lists.keys():
        docuement_frequency[key] = len(posting_lists[key])
    merged_posting_list = merge_posting_list(posting_lists)
    # print(merged_posting_list)
    titles, extracted_info = process_posting_list(merged_posting_list,docuement_frequency,count=10,  special=True)
    if( len(titles) < 11):
        titles, extracted_info = process_posting_list(posting_lists, docuement_frequency,count=10, special=True)
    
    del posting_lists


    title_category = {}
    for arr in extracted_info:
        title_category[arr[0]] = arr[1:]

    count = 0
    # print(titles)
    # print(extracted_info[:10])
    # print()
    ans = []
    k = min(len(titles), 10)
    # print("PRINTING TITLES: ", titles)
    for title in titles:
        if(title == 0):
            continue
        categories = title_category[title]
        # print(categories)
        word = categories[6]
        word_c = word_cat[word]
        ind = category_index[word_c]
        # print(title)
        # if categories[ind] > 0:
            
        curr_title = get_title(title-1)
        ans.append(curr_title)
        count+=1
        if count == k:
            break
    del titles, extracted_info
    writetofile(ans)
    

            




with open(queries, 'r') as f:
    ind = 0
    while(True):
        query = f.readline().strip("\n")
        query = query.lower()
        t3 = time.time()
        ind+=1
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
            docuement_frequency = {}
            for key in posting_lists.keys():
                docuement_frequency[key] = len(posting_lists[key])
            merged_list = merge_posting_list(posting_lists)
            # print(merged_list)
            output = process_posting_list(merged_list,docuement_frequency, 10)
            
            
            del merged_list
            del docuement_frequency
            del posting_lists

            count = 0
            ans = []
            k = min(10, len(output))
            for title in output:
                curr_title = get_title(title-1)
                ans.append(curr_title)
                count+=1
                if count == 10:
                    break
            writetofile(ans)
        t4 = time.time()
        print("query {} completed in: ".format(ind), t4-t3)

t2 = time.time()
print("TOTAL TIME TAKEN: ", t2-t1)
    


    