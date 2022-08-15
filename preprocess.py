from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import re


class Preprocess():
    def __init__(self):
        self.wiki_pattern_matching = {
            "information": "{{information",
            "infobox" : "{{Infobox",
            "category" : "\[\[Category:\s*(.*?)\]\]",
            "wiki_links": "\[\[(.*?)\]\]",
            "comments" : "<--.*?-->",
            "styles" : "\[\|.*?\|\]",
            "curly_braces": "{{.*?}}",
            "square_braces": "\[\[.*?\]\]",
            "references": "<ref>.*?</ref>",
            "url": "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "www": "www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        }
        self.stopwords = self.getStopWords()
        self.ps = PorterStemmer()
        self.externalLinksPattern = r'==External links==\n[\s\S]*?\n\n'
        self.referencesPattern = r'== ?references ?==(.*?)\n\n' #r'==References==\n[\s\S]*?\n\n'
        self.removeSymbolsPattern = r"[~`!@#$%-^*+{\[}\]\|\\<>/?]"
  
    def tokenise(self, data):
        tokens = data.split()
        return tokens


    def getStopWords(self):
        stopwords = set()
        file1 = open('stopwords.txt', 'r')
        Lines = file1.readlines()
        for line in Lines:
                stopwords.add(line[0:-1])
        return stopwords

    def stemmer(self, data):
        
        stemmed_data = []
        for word in data.split():
            stemmed_data.append(self.ps.stem(word))
        return " ".join(stemmed_data)

    def remove_all_tags(self, wiki_content):
        tag_regex = re.compile("<.*?>")
        return re.sub(tag_regex, '', wiki_content)

    def remove_all_urls(self, wiki_content):
        regex = re.compile(self.wiki_pattern_matching["url"])
        wiki_content = re.sub(regex, ' ', wiki_content)
        regex = re.compile(self.wiki_pattern_matching["www"])
        wiki_content = re.sub(regex, ' ', wiki_content)
        return wiki_content
    def strip_footers(self, content):
        labels = ["references", "further reading", "see also", "notes"]
        for l in labels:
            regex = "==%s==" % (labels)
            found = re.search(regex, content)
            if found is not None:
                content = content[0:found.start()-1]
        return content 

    def filter_content(self, content):
        filters = set(['(', '{', '[', ']', '}', ')', '=', '|', '?', ',', '+', '\'', '\\', '*', '#', ';', '!', '\"', '%', '.', '-', '*'])
        content = content.strip()
        if len(content) == 0:
            return content
        # if len(set(content).intersection(filters)) == 0:
        #     return content
        for elem in filters:
            content = content.replace(elem, ' ')
        return content
    
    def get_content_body(self, wiki_content):
        # regex = re.compile(self.wiki_pattern_matching["comments"])
        # new_content = re.sub(regex, ' ', wiki_content)
        regex = re.compile(self.wiki_pattern_matching["styles"])
        new_content = re.sub(regex, ' ', wiki_content)
        regex = re.compile(self.wiki_pattern_matching["references"])
        new_content = re.sub(regex, ' ', new_content)
        new_content = self.remove_all_tags(new_content)
        regex = re.compile(self.wiki_pattern_matching["curly_braces"])
        new_content = re.sub(regex, ' ', new_content)
        regex = re.compile(self.wiki_pattern_matching["square_braces"])
        new_content = re.sub(regex, ' ', new_content)
        
        new_content = self.remove_all_urls(new_content)

        new_content = self.strip_footers(new_content)
        return new_content

    def getInfobox(self, data):
        startIndex = data.find(self.wiki_pattern_matching["infobox"])
        open = 0
        if len(data) == 0:
            return ""
        infobox = ""
        for i in range(startIndex, len(data)):
            if data[i] == '{':
                open+=1;
            elif(data[i] == '}'):
                open-=1
            else:
                infobox+=data[i]
            if open == 0:
                break
        return infobox, i

    def getCategory(self, wiki_content):
        category_regex = re.compile(self.wiki_pattern_matching["category"], re.IGNORECASE)
        result_string = re.findall(category_regex, wiki_content)
        result_string = ''.join(result_string)
        # result_string = self.remove_all_urls(result_string)
        # new_wiki_content = re.sub(category_regex, '', wiki_content)
        return result_string

    def getBody(self, startIndex, data):
        if len(data) <= startIndex:
            # print("INVALID START INDEX")
            return ""
        labels = [" References ", "Further reading", "See also", " Notes ", "References", " External links "]
        endIndex = float("inf")
        for label in labels:
            reg = "=={}==".format(label)
            ind = data.find(reg)
            if(ind > startIndex):
                endIndex = min(endIndex, ind)

        if endIndex >= len(data):
            # print("INVALID END INDEX")
            return ""

        body = data[startIndex:endIndex] 
        return body

    def remove_stopwords(self, data):
        for word in self.stopwords:
            if word in data:
                data.replace(word, "")
        return data

    def finalProcessing(self, data):
        if len(data) > 0:
            processed = self.filter_content(data)
            processed = self.get_content_body(processed)
            processed = self.stemmer(processed)
            processed = self.remove_stopwords(processed)
            temp = processed.split()
            return " ".join(temp)
        return ""

    def processExternalLinksData(self, data):
        links = re.findall(self.externalLinksPattern, data, flags= re.IGNORECASE)
        links = " ".join(links)
        links = links[20:]
        links = re.sub('[|]', ' ', links)
        links = re.sub('[^a-zA-Z ]', ' ', links)
        # self.external_links_dict = self.basicProcessing(links)  
        return links

    def processReferences(self, data):
        references = re.findall(self.referencesPattern, data, flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
        references = ' '.join(references)
        references = re.sub(self.removeSymbolsPattern, ' ', references)
        # self.references_dict = self.basicProcessing(references)  
        return references