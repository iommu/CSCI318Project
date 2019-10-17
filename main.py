#!/usr/bin/python3

import re
import csv
import requests
from bs4 import BeautifulSoup

# Base URL for searching google scholar
url = "https://scholar.google.com/scholar?"
# Add query to base url string
search = input("Search query : ")
searchReplace = [" ",",",":","-"]

results = [[""]*len(searchReplace)]
line = 1

with open(search + ".csv", 'w', newline='') as csvFile:
    dataWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for count, rep in enumerate(searchReplace,0):
        searchEdit = search.replace("<>",rep)
        results[0][count] = searchEdit
        print("\nSearching for " + str(searchEdit) + "\n")
        for page in range(0,1):
            request = requests.get(url+"lr=lang_en&start="+str(page*10)+"&q="+searchEdit)
            soup = BeautifulSoup(request.content, features="html.parser")

            papers = []
            papersHTML = soup.find_all("div", {"class": "gs_ri"})
            print("\nPAGE " + str(page+1) + "\n")
            for countPapers, paperHTML in enumerate(papersHTML,1):
                try:
                    print(paperHTML.select_one("h3 a").text)
                    cited = paperHTML.select_one("div:nth-of-type(3) a:nth-of-type(3)").text
                    print(cited)
                    if countPapers+1 > line:
                        results.append([""]*len(searchReplace))
                        line += 1
                    results[countPapers][count] = int(re.search(r'\d+', cited).group())
                except:
                    pass
    dataWriter.writerows(results)