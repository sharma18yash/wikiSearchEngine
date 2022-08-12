from concurrent.futures import thread
from re import S
from unicodedata import category
import xml.sax
import sys
import preprocess
import time
import json
import threading

print("running without stemmer")
documents_indexed = 0
global_index = dict()


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


    def finalProcessing1(self, data, tag):
        if len(data) > 0:
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            # processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.body_list.append(processed)
            self.body_list = processed
        else:
            # self.body_list.append("")
            self.body_list = ""

    def finalProcessing2(self, data, tag):
        if len(data) > 0:
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            # processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.infobox_list.append(processed)
            self.infobox_list = processed
        else:
            # self.infobox_list.append("")
            self.infobox_list = ""

    def finalProcessing3(self, data, tag):
        if len(data) > 0:
            processed = self.pre.filter_content(data)
            processed = self.pre.get_content_body(processed)
            # processed = self.pre.stemmer(processed)
            processed = self.pre.remove_stopwords(processed)
            # self.category_list.append(processed)
            self.category_list = processed
        else:
            # self.category_list.append("")
            self.category_list = ""
    

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
                title_data = self.pre.filter_content(self.titleData)
                self.title_list = title_data
            else:
                self.title_list = ""
            self.titleData = ""
            # self.count+=1
            self.isTitle = False
            self.haveTitle = True
        if(self.isText == True):
            if(len(self.textData) > 0):
                infobox, endIndex = self.pre.getInfobox(self.textData)
                body = self.pre.getBody(endIndex, self.textData)
                category = self.pre.getCategory(self.textData)
                t1 = threading.Thread(target = self.finalProcessing2, args=(infobox, 1) )
                t2 = threading.Thread(target = self.finalProcessing1, args=(body, 1) )
                t3 = threading.Thread(target = self.finalProcessing3, args=(category, 1) )
                t1.start()
                t2.start()
                t3.start()

                t1.join()
                t2.join()
                t3.join()
                self.isText = False
                self.count+=1
                self.textData = ""
                self.haveText = True
        
        
        # if(self.count == 10000):
       
        if self.haveTitle and self.haveText:
            # print("TITLE", self.title_list)
            # print("INFOBOX", self.infobox_list)
            # print("BODY", self.body_list)
            # print("CATEGORY", self.category_list)
            self.create_index()
            self.haveText = False
            self.haveTitle = False
        
        
        # self.count = 0
            self.title_list = ""
            self.infobox_list = ""
            self.body_list = ""
            self.category_list = ""
        # print(documents_indexed)
        
        
        # global documents_indexed
        

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
        # if len(self.title_list) != len(self.infobox_list) or len(self.infobox_list) != len(self.body_list) or len(self.body_list) != len(self.category_list):
            # print( len(self.title), len(self.infobox), len(self.category), len(self.body))
            # print("INVALID INPUT")
            # exit(0)
        
        global documents_indexed
        global global_index
        # for i in range(len(self.title)):
        documents_indexed+=1
        title_index = self.create_dict(self.title_list)
        info_index = self.create_dict(self.infobox_list)
        body_ind = self.create_dict(self.body_list)
        cat_ind = self.create_dict(self.category_list)

        # print("TITLE: ", title_index)
        # print("INFOBOX: ", info_index)
        # print("BODY: ",body_ind )
        # print("CATEGORY: ", cat_ind)

        all_data = self.title_list + " " + self.infobox_list + " " + self.body_list + " " + self.category_list
        all_data = set(all_data.split())
        # print("ALL DATA: ", all_data)
        
        for word in all_data:
            count = ""
            count = count+"d{}".format(documents_indexed)
            if word in title_index:
                count = count + "-t{}".format(title_index[word])

            if word in info_index:
                count = count + "-i{}".format(info_index[word])
            
            if word in body_ind:
                count = count + "-b{}".format(body_ind[word])
            
            if word in cat_ind:
                count = count + "-c{}".format(cat_ind[word])

            count+="|"
            if word in global_index:
                global_index[word] += count
            else:
                global_index[word] = count

        if(documents_indexed % 100000 == 0):
            print(documents_indexed)


if ( __name__ == "__main__"):
    
    t1 = time.time()
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = wikiHandler()
    parser.setContentHandler( Handler )
    parser.parse(sys.argv[1])
    t2 = time.time()
    
    print("DOCUMENTS INDEXED: ", documents_indexed)
    with open('index.txt', 'w') as index_file:
        index_file.write(json.dumps(global_index))

    print(len(global_index))
    print("PARSING COMPLETED IN SECONDS: ", t2 - t1)