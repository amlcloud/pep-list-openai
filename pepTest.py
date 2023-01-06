from pepOpenAi import PepOpenAi

testUrl = "https://www.airforce.gov.au/about-us/leadership/"

# First we test if it does run through and gives a list of names
# CONCLUSION: it does, but needs more iterations for higher precision
testPep = PepOpenAi()
testPep.getLongestNamesList(testUrl, 50)
print(testPep.names)

# Then we check the list of names and get data on each of them
testPep.getNamesData()
print(testPep.data)

# Then save the csv file
testPep.savePepCsv("C:/Users/kilik/Documents/COLLEGE/AML/pep_csv/test.csv")
