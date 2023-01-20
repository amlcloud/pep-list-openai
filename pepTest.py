from pepOpenAi import PepOpenAi
from config import path
import time

st = time.time()

testUrl = "https://www.airforce.gov.au/about-us/"
EN_NAMES = ['CA', 'GB', 'US']

# First we test if it does run through and gives a list of names
# CONCLUSION: it does, but needs more iterations for higher precision
# testPep = PepOpenAi(filtered_countries=EN_NAMES)
testPep = PepOpenAi(filtered_countries=None)
testPep.getLongestNamesList(testUrl, 3)
print(testPep.names)

# EXTRA STEP: Filter the list of names to make sure they really are just
# A list of names
testPep.filterNames()
print(testPep.names)
# print("Length: "+str(len(testPep.names)))
# print("FILTERED NAMES")
# print(testPep.names)

# EXTRA STEP: Verify if each name is indeed a PEP or not, some
# names generated are fake
testPep.verifyNames()
print(testPep.names)

# PROBLEM: AT THIS POINT TOO MANY REQUESTS, SO OPENAI STOPS
# Then we check the list of names and get data on each of theme
testPep.getNamesData()
print(testPep.data)

# Then save the csv file
# Change path name to fit your pc
testPep.savePepCsv(path)

et = time.time()
elapsed_time = et - st
print("Execution Time: "+str(elapsed_time)+" seconds")
