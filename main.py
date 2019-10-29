#!/usr/bin/python3
# The code for get and searchQuery functions is modified from the pymed project
# https://github.com/gijswobben/pymed
# Copyright (c) 2018 Gijs Wobben
# Copyright (c) 2019 Alex Carter
import requests
import csv
import lxml.html
import time

# Store the input parameters
tool = "MyTool"
email = "my@email.address"
sort = "relevance"

# Define the default query parameters
parameters = {"tool": tool, "email": email,
              "db": "pubmed", "retmode": "json", "sort": sort}


def get(url, parameters):
    for i in range(0, 2):
        # Make the request to PubMed
        response = requests.get(
            f"https://eutils.ncbi.nlm.nih.gov{url}", params=parameters)
        # Check for any errors and break if none
        try:
            response.raise_for_status()
        # If fail try again once
        except requests.exceptions.HTTPError as e:
            print(f"Request error, retying {i-1} more times")
            continue
        break
    return response.json()


def searchQuery(query, maxResults=100):
    # Create a placeholder for the retrieved IDs
    articles = []
    # Add specific query parameters
    parameters["term"] = query
    parameters["retmax"] = 50000
    # Calculate a cut off point based on the maxResults parameter
    if maxResults < 50000:
        parameters["retmax"] = maxResults
    # Make the first request to PubMed
    response = get(url="/entrez/eutils/esearch.fcgi", parameters=parameters)
    # Add the retrieved IDs to the list
    articles += response.get("esearchresult", {}).get("idlist", [])
    # Get information from the response
    totalResultCount = int(response.get("esearchresult", {}).get("count"))
    retrievedCount = int(response.get("esearchresult", {}).get("retmax"))
    # If not all articles are retrieved, continue to make requests until we have everything
    while retrievedCount < totalResultCount and retrievedCount < maxResults:
        # Calculate a cut off point based on the maxResults parameter
        if (maxResults - retrievedCount) < parameters["retmax"]:
            parameters["retmax"] = maxResults - retrievedCount
        # Start the collection from the number of already retrieved articles
        parameters["retstart"] = retrievedCount
        # Make a new request
        response = get(url="/entrez/eutils/esearch.fcgi",
                       parameters=parameters)
        # Add the retrieved IDs to the list
        articles += response.get("esearchresult", {}).get("idlist", [])
        # Get information from the response
        retrievedCount += int(response.get("esearchresult", {}).get("retmax"))
    # Return article IDs
    return articles


# Create search terms array
batchSearch = ["vaccine", "DNA", "mitochondria", "role", "medication", "pill",
               "cancer", "liver", "brain", "skin", "virus", "germ", "bacteria",
               "flu", "drug", "blood", "design", "aging", "health", "heart"]

for search in batchSearch:
    print(f"Searching for {search}")
    # Open write file and write the csv header
    with open(search + ".csv", 'w', newline='') as csvFile:
        dataWriter = csv.writer(csvFile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        dataWriter.writerow(["name", "cited"])
        # Request batch IDs
        results = searchQuery(search, maxResults=500)
        # For each paper ID
        for pmid in results:
            for i in range(0, 2):
                # Get citation count of paper
                citation = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id=" + pmid)
                try:
                    citation.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    # If fail try again once
                    print(f"Error in getting citation, retrying {i-1} times")
                    continue
                # Get name of paper
                name = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=" + pmid)
                try:
                    name.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    # If fail try again once
                    print(f"Error in getting name, retrying {i-1} times")
                    continue
                break
            citationXML = lxml.html.fromstring(citation.content)
            nameXML = lxml.html.fromstring(name.content)
            # Write name, citation count to csv file
            dataWriter.writerow([nameXML.xpath(
                "//item[@name='Title']")[0].text, int(citationXML.xpath("count(//link)"))])
            # Sleep so we don't cause server to trigger cooldown period
            time.sleep(1)

# Split section
# For each csv name created from above
for file in batchSearch:
    # Open a new .csv for the final output
    with open(file + "Split.csv", 'w', newline='') as writeFile:
        csvWriter = csv.writer(writeFile, delimiter=',',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Write the initial header
        csvWriter.writerow(["comma", "colon", "semicolon", "dash", "none"])
        # Init a counter for how many instances in every column for calculating averages
        finalCount = [0, 0, 0, 0, 0]
        # Open a the old .csv file with "name, citation count" content
        with open(file + ".csv", newline='') as readFile:
            csvReader = csv.reader(readFile, delimiter=',', quotechar='"')
            # Skip header
            next(csvReader, None)
            # For each row in the file
            for row in csvReader:
                contains = False
                # Create the row array
                tempCount = ["", "", "", "", ""]
                # Search for specific chars in the name
                if "," in str(row[0]):
                    # If char is in name then write the citation count to it's relevant position in the column
                    tempCount[0] = str(row[1])
                    # Increment the counter for this column
                    finalCount[0] += 1
                    # Set boolean to True
                    contains = True
                if ":" in str(row[0]):
                    tempCount[1] = str(row[1])
                    finalCount[1] += 1
                    contains = True
                if ";" in str(row[0]):
                    tempCount[2] = str(row[1])
                    finalCount[2] += 1
                    contains = True
                if "-" in str(row[0]):
                    tempCount[3] = str(row[1])
                    finalCount[3] += 1
                    contains = True
                # If boolean was never set to True then the title contains no special characters
                if not contains:
                    tempCount[4] = str(row[1])
                    finalCount[4] += 1
                # Write this row to file
                csvWriter.writerow(tempCount)
            # Write the counter to file
            csvWriter.writerow(finalCount)
