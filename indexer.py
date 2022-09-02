from concurrent.futures import thread
from re import S
from unicodedata import category
import xml.sax
import sys
import preprocess
import time
import json
import threading
from collections import OrderedDict
import filehandling
import os


documents_indexed = 0
global_index = dict()
index_count = 0
all_title = []
folder_name = sys.argv[2]
stat_file = sys.argv[3]
total_keywords=0
total_indexed_words=0


class wikiHandler( xml.sax.ContentHandler):
    def __init__(self) -> None:
        self.titleData = ""
        self.textData = ""
        self.isTitle = False
        self.isText = False
        self.count = 0
        # self.docid = 0
        self.title_list = ""
        self.body_list = ""
        self.category_list = ""
        self.infobox_list = ""
        self.pre = preprocess.Preprocess()
        self.haveTitle = False
        self.haveText = False
        print("INDEXING STARTED")


    def finalProcessing1(self, data, tag):
        if len(data) > 0:
            # data = data.lower()
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            processed = processed.lower()
            processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.body_list.append(processed)
            # x = processed.split()
            self.body = processed
        else:
            # self.body_list.append("")
            self.body = ""

    def finalProcessing2(self, data, tag):
        if len(data) > 0:
            data = data.lower()
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            processed = processed.lower()
            processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.infobox_list.append(processed)
            # x = processed.split()
            self.infobox = processed
        else:
            # self.infobox_list.append("")
            self.infobox = ""

    def finalProcessing3(self, data, tag):
        if len(data) > 0:
            data = data.lower()
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            processed = processed.lower()
            processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.category_list.append(processed)
            # x = processed.split()
            self.category = processed
        else:
            # self.category_list.append("")
            self.category = ""
    def finalProcessing4(self, data, tag):
        if len(data) > 0:
            data = data.lower()
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            processed = processed.lower()
            processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.category_list.append(processed)
            # x = processed.split()
            self.external_links = processed
        else:
            # self.category_list.append("")
            self.external_links = ""
    
    def finalProcessing5(self, data, tag):
        if len(data) > 0:
            data = data.lower()
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            processed = processed.lower()
            processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.category_list.append(processed)
            # x = processed.split()
            self.references = processed
        else:
            # self.category_list.append("")
            self.references = ""
        
    

    def startElement(self, tag, attrs):
        # self.textData = ""
        # self.titleData = ""
        if(tag == "title"):
            self.isTitle = True
        if(tag == "text"):
            self.isText = True

    def endElement(self, name):
        
        if(self.isTitle == True):
            if(len(self.titleData) > 0):
                # self.title = self.titleData
                self.title = self.pre.finalProcessing(self.titleData)
            else:
                self.title = ""
            self.titleData = ""
            # self.count+=1
            self.isTitle = False
            self.haveTitle = True
        if(self.isText == True):
            if(len(self.textData) > 0):
                temp_infobox, endIndex = self.pre.getInfobox(self.textData)
                temp_body = self.pre.getBody(endIndex, self.textData)
                temp_category = self.pre.getCategory(self.textData)
                temp_links =    self.pre.processExternalLinksData(self.textData)
                temp_references = self.pre.processReferences(self.textData)
                t1 = threading.Thread(target = self.finalProcessing2, args=(temp_infobox, 1) )
                t2 = threading.Thread(target = self.finalProcessing1, args=(temp_body, 1) )
                t3 = threading.Thread(target = self.finalProcessing3, args=(temp_category, 1) )
                t4 = threading.Thread(target = self.finalProcessing4, args=(temp_links, 1) )
                t5 = threading.Thread(target = self.finalProcessing5, args=(temp_references, 1) )
                t1.start()
                t2.start()
                t3.start()
                t4.start()
                t5.start()

                t1.join()
                t2.join()
                t3.join()
                t4.join()
                t5.join()
                self.isText = False
                self.count+=1
                self.textData = ""
                self.haveText = True
       
        if self.haveTitle and self.haveText:

            self.create_index()
            self.haveText = False
            self.haveTitle = False
        
        
            self.title_list = ""
            self.infobox_list = ""
            self.body_list = ""
            self.category_list = ""
            self.external_links = ""
            self.refernces = ""

        

    def characters(self, content):
        if(self.isTitle == True):
            self.titleData += content
        if(self.isText == True):
            self.textData += content

    def create_dict(self, data):
        dictionary = {}
        for word in data.split():
            if word in dictionary:
                dictionary[word]+=1
            else:
                dictionary[word] = 1
        return dictionary
    
    def create_index(self):
        if len(self.title_list) != len(self.infobox_list) or len(self.infobox_list) != len(self.body_list) or len(self.body_list) != len(self.category_list):
            # print( len(self.title), len(self.infobox), len(self.category), len(self.body))
            print("INVALID INPUT")
            exit(0)
        
        global documents_indexed
        global global_index
        global all_title
        global total_keywords
        documents_indexed+=1
        all_title.append(self.title)
        title_index = self.create_dict(self.title)
        info_index = self.create_dict(self.infobox)
        body_ind = self.create_dict(self.body)
        cat_ind = self.create_dict(self.category)
        ref_ind = self.create_dict(self.references)
        exernal_ind = self.create_dict(self.external_links)

        # print("TITLE: ", title_index)
        # print("INFOBOX: ", info_index)
        # print("BODY: ",body_ind )
        # print("CATEGORY: ", cat_ind)

        all_data = self.title + " " + self.infobox + " " + self.body + " " + self.category+ " " + self.references + " " + self.external_links
        all_data = set(all_data.split())
        total_keywords += len(all_data)
        # print("ALL DATA: ", all_data)
        
        for word in all_data:
            count = ""
            # count = count+"d{}".format(documents_indexed)
            flag = False
            if word in title_index:
                flag = True
                count = count + "-t{}".format(title_index[word])

            if word in info_index:
                flag = True
                count = count + "-i{}".format(info_index[word])
            
            if word in body_ind:
                flag = True
                count = count + "-b{}".format(body_ind[word])
            
            if word in cat_ind:
                flag = True
                count = count + "-c{}".format(cat_ind[word])

            if word in ref_ind:
                flag = True
                count = count + "-r{}".format(ref_ind[word])

            if word in exernal_ind:
                flag = True
                count = count + "-e{}".format(exernal_ind[word])

        
            if flag:
                count = "d{}".format(documents_indexed) + count
                count = count + "|"
            if word in global_index:
                global_index[word] += count
            elif(len(count) > 2):
                global_index[word] = count

        global index_count
        global folder_name
        global total_indexed_words
        if(documents_indexed % 100000 == 0 and documents_indexed != 0):
            print(documents_indexed, "len = ", len(global_index))
            new_index = OrderedDict(sorted(global_index.items()))
            total_indexed_words += len(new_index)
            # with open('{}/index{}.txt'.format(folder_name, index_count), 'w') as index_file:
            #     index_file.write(json.dumps(new_index))

            with open('{}/index{}.txt'.format(folder_name, index_count), 'w') as f: 
                for key, value in new_index.items(): 
                    f.write('%s~%s\n'% (key, value))
            global_index = dict()
            index_count+=1



if ( __name__ == "__main__"):
    
    t1 = time.time()
    wikidump = sys.argv[1]
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = wikiHandler()
    parser.setContentHandler( Handler )
    parser.parse(wikidump)
    
    new_index = OrderedDict(sorted(global_index.items()))
    total_indexed_words += len(new_index)

    print("DOCUMENTS INDEXED: ", documents_indexed)
    with open('{}/index{}.txt'.format(folder_name, index_count), 'w') as f: 
        for key, value in new_index.items(): 
            f.write('%s~%s\n'% (key, value))

    
    
    with open('final/title_list.txt'.format(folder_name), 'w') as title_file:
        title_file.write(json.dumps(all_title))
    t2 = time.time()

    # write total_indexed_words and total_keywords to file
    with open('{}'.format(stat_file), 'w') as total_indexed_words_file:
        total_indexed_words_file.write(str(total_keywords))
        total_indexed_words_file.write(str("\n"))
        total_indexed_words_file.write(str(total_indexed_words))
    print("PARSING COMPLETED IN SECONDS: ", t2 - t1)
    print("tmp files created: ", index_count)

    # print("MERGING FILES")
    # fh = filehandling.file_handling(index_count)
    # secondary_index_files = fh.merge()
    # print("SECONDARY FILES CREATED: ", secondary_index_files )

    # print("REMVOVING TEMPORARY FILES")

    # for i in range(0, index_count):
    #     os.remove("tmp/index{}.txt".format(i))