# Need the following imports

import openai
import csv
import re

openai.api_key = "sk-Hzh7Acu2VFQWZp0FWpcnIPzkHIuii0e9n2am7PHU"

class PepOpenAi:

    # TODO: Add variables that you might need
    def __init__(self):
        self.names = []
        self.data = "Name;Date of Birth;Country;Current Position\n"
        return

    def getNames(self, url):
        # Promp that will be used to get the list of names of PEPs
        textPrompt = "Create a CSV of the given names (wihtout their position) of Politically Exposed Persons (PEPs) in this URL in the format Index, Name: "
        
        try:
            namesResponse = openai.Completion.create(
                model="text-davinci-002",
                prompt= textPrompt + url,
                temperature=0.7,
                max_tokens=700,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Extract the names 
            namesQuery = namesResponse['choices'][0]['text']
        
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
        
        except:
            return []

    # Just uses getNames() to return the longest possible list
    # created from the query
    def getLongestNamesList(self, url, iterations=50):
        maxLen = -1
        returnText = ""
        for i in range(iterations):
            currResponse = self.getNames(url)
            if len(currResponse) > maxLen:
                maxLen = len(currResponse)
                returnText = currResponse

        # Don't know if I need this yet
        # RIGHT NOW: Likely we only start adding names
        # to the class when we are getting longest list of names
        self.names = self.names + currResponse
        return currResponse
    
    # This gets a list of URLs and gets the longest
    # List of names of each and puts them in the names attribute
    def getUrlNames(self, urlList, iterations=50):
        for url in urlList:
            self.getLongestNamesList(url, iterations)

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

            dataText = dataQuery['choices'][0]['text']

            # Have to adjust the the string so that it can
            # be put as a CSV
            while dataText[0] == '\n':
                dataText = dataText[1:]
            dataText = re.sub("; ", ";", dataText)
            dataText = re.sub(r'\n+', '\n', dataText)

            # Now append string to data attribute
            self.data = self.data + dataText + '\n'
            currList = currList[loopWeight:]
    
    def savePepCsv(self, path):
        with open(path, 'w') as f:
            writer = csv.writer(f)
            # First extract each row of the data
            dataList = self.data.split("\n")
            # Now put each row as a list into the csv
            for item in dataList:
                writer.writerow(item.split(";"))
    
