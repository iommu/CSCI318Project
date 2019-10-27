#!/usr/bin/python3
import datetime
import requests
import csv
import lxml.html
import time

# Base url for all queries
BASE_URL = "https://eutils.ncbi.nlm.nih.gov"

# Store the input parameters
tool = "MyTool"
email = "my@email.address"

# Define the standard / default query parameters
parameters = {"tool": tool, "email": email, "db": "pubmed"}

def get(id):
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=protein&id=" + id)
    xml = lxml.html.fromstring(response.content)
    print(xml.xpath("count(//title)"))


def get(url: str, parameters: dict, output: str = "json"):

    # Set the response mode
    parameters["retmode"] = output

    # Make the request to PubMed
    response = requests.get(f"{BASE_URL}{url}", params=parameters)

    # Check for any errors
    response.raise_for_status()

    # Return the response
    if output == "json":
        return response.json()
    else:
        return response.text

def searchQuery(query, max_results = 100) -> list:
    # Create a placeholder for the retrieved IDs
    articles = []

    # Add specific query parameters
    parameters["term"] = query
    parameters["sort"] = "relevance"
    parameters["retmax"] = 50000

    # Calculate a cut off point based on the max_results parameter
    if max_results < parameters["retmax"]:
        parameters["retmax"] = max_results


    # Make the first request to PubMed
    response = get(url="/entrez/eutils/esearch.fcgi", parameters=parameters)

    # Add the retrieved IDs to the list
    articles += response.get("esearchresult", {}).get("idlist", [])

    # Get information from the response
    total_result_count = int(response.get("esearchresult", {}).get("count"))
    retrieved_count = int(response.get("esearchresult", {}).get("retmax"))

    # If no max is provided (-1) we'll try to retrieve everything
    if max_results == -1:
        max_results = total_result_count

    # If not all articles are retrieved, continue to make requests untill we have everything
    while retrieved_count < total_result_count and retrieved_count < max_results:

        # Calculate a cut off point based on the max_results parameter
        if (max_results - retrieved_count) < parameters["retmax"]:
            parameters["retmax"] = max_results - retrieved_count

        # Start the collection from the number of already retrieved articles
        parameters["retstart"] = retrieved_count

        # Make a new request
        response = get(
            url="/entrez/eutils/esearch.fcgi", parameters=parameters
        )

        # Add the retrieved IDs to the list
        articles += response.get("esearchresult", {}).get("idlist", [])

        # Get information from the response
        retrieved_count += int(response.get("esearchresult", {}).get("retmax"))

    # Return the response
    return articles

# Base URL for searching google scholar
url = "https://scholar.google.com/scholar?"
# Add query to base url string
search = input("Search query : ")

with open(search + ".csv", 'w', newline='') as csvFile:
    dataWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    dataWriter.writerow(["name","cited"])
    results = searchQuery(search, max_results=500)
    for pmid in results:
        citation = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id=" + pmid)
        citationXML = lxml.html.fromstring(citation.content)
        name = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=" + pmid)
        nameXML = lxml.html.fromstring(name.content)
        dataWriter.writerow([nameXML.xpath("//item[@name='Title']")[0].text,int(citationXML.xpath("count(//link)"))])
        time.sleep(1)