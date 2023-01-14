# Need the following imports

import openai
import config
import csv
import re
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from time import sleep
import logging

class PepOpenAi:

    # TODO: Add variables that you might need
    def __init__(self):
        self.names = []
        self.data = "Name;Date of Birth;Country;Current Position\n"
        self.logger = logging.getLogger('ftpuploader')
        return

    def getNames(self, url):
        # Promp that will be used to get the list of names of PEPs
        textPrompt = "Create a CSV of the given names (wihtout their position) of Politically Exposed Persons (PEPs) in this URL in the format Index, Name: "
        
        try:
            # Extract the names 
            namesQuery = self.makeGPTQuery(textPrompt+url)
        
            # Need to format the csv file so that everything looks clean
            STARTING_CHAR = '1'
            while namesQuery[0] != STARTING_CHAR:
                namesQuery = namesQuery[1:]

            NAME_HEADER = "Index,Name\n"
            if namesQuery.split("\n")[0] != NAME_HEADER[:10]:
                namesQuery = NAME_HEADER + namesQuery

            namesQuery = re.sub(", ", ",", namesQuery)
        
            # Now get the names you want to add and return them
            return [item[2:] for item in namesQuery.split("\n")[1:]]
        
        except Exception as e:
            self.logger.error("Failed to make list "+str(e))
            return []

    # Just uses getNames() to return the longest possible list
    # created from the query
    def getLongestNamesList(self, url, iterations=50):
        # maxLen = -1
        # newList = []
        # returnText = ""
        for i in range(iterations):
            currResponse = self.getNames(url)
            # print("CurrResponse:" + str(currResponse))
            for item in currResponse:
                # print("Item: "+item)
                # item = item.strip(',').upper()
                item = item.strip(',')
                item = item.strip(' ')
                item = item.strip("\n")
                if not item in self.names:
                    self.names.append(item)
            print("Current Iteration: "+str(i))
            print(self.names)
        # Don't know if I need this yet
        # RIGHT NOW: Likely we only start adding names
        # to the class when we are getting longest list of names
        # self.names = self.names + currResponse
        # self.names = newList
        # return currResponse
        return
    
    # This gets a list of URLs and gets the longest
    # List of names of each and puts them in the names attribute
    def getUrlNames(self, urlList, iterations=50):
        for url in urlList:
            self.getLongestNamesList(url, iterations)
        return

    # Possible function to filter out only the names in
    # the text
    def filterNames(self):
        newNames = []
        self.names = [item for item in self.names if ' ' in item]
        self.names = list(set(self.names))
        print("NEW NAMES: "+str(self.names))
        for name in self.names:
            name = name + " is a person."
            # More details of this method on: https://unbiased-coder.com/extract-names-python-nltk/
            nltk_results = ne_chunk(pos_tag(word_tokenize(name)))
            for item in nltk_results:
                if type(item) == Tree:
                    new = ''
                    for nltk_result_leaf in item.leaves():
                        new += nltk_result_leaf[0] + ' '
                    newNames.append(new.strip())
                    print ('Type: ', nltk_results.label(), 'Name: ', new)
            sleep(3)
        self.names = newNames
        return
    
    # Possible function to test if name really is a PEP
    def verifyNames(self):
        instances = 0
        newNames = []
        textPrompt = " a Politically Exposed Person? Answer with 'Yes' or 'No'."
        for name in self.names:
            try:
                ans = self.makeGPTQuery("Is "+name+textPrompt).strip('\n')
                ans = ans.strip()
                print("Is " + name + " a PEP? Answer: "+ans)
                if ans == 'Yes':
                    newNames.append(name)
                instances = instances + 1
            except Exception as e:
                print("Unable to do request for "+name)
                self.logger.error('Error in request '+str(e))
                # Print reason why request did not work
                pass
            sleep(3)
        self.names = newNames
        print("Number of Instances: "+str(instances))
        return

    # Once you have the names covered, you should be able
    # to get the needed data 
    def getNamesData(self, loopWeight=1):
        dataPrompt = "Get the Name, Date of Birth, Country, Current Position of the following people and put in a semicolon delimited CSV format: "
        currList = self.names
        # Run through the list and get the data
        while currList:
            # Current round of additions,
            # Response from ai compromises when too many entries
            # at a time
            currAdd = currList[:loopWeight]
            dataQuery = openai.Completion.create(
                model="text-davinci-002",
                # prompt= infoPrompt_1+listNames,
                prompt= dataPrompt+str(currAdd),
                temperature=0.7,
                max_tokens=700,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Have to adjust the the string so that it can
            # be put as a CSV
            dataText = self.makeGPTQuery(dataPrompt+str(currAdd)).strip('\n')
            dataText = dataText.strip()
            print(dataText)

            # Now append string to data attribute
            self.data = self.data + dataText + '\n'
            currList = currList[loopWeight:]
            sleep(15)
        return

    # Helper function to make openai queries
    def makeGPTQuery(self, currPrompt):
        try:
            query = openai.Completion.create(
                model="text-davinci-002",
                prompt= currPrompt,
                temperature=0.7,
                max_tokens=700,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            currResponse = query['choices'][0]['text']
            query = query.strip('\n')
            query = query.strip() 
            return query

        except Exception as e:
            self.logger.error("Query could not be processed because: "+str(e))
            return ""
    
    def savePepCsv(self, path):
        with open(path, 'w') as f:
            writer = csv.writer(f)
            # First extract each row of the data
            dataList = self.data.split("\n")
            # Now put each row as a list into the csv
            for item in dataList:
                writer.writerow(item.split(";"))
        return
    
