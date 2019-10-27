import csv

file = input("Input .csv file name : ")

with open(file + "Split.csv", 'w', newline='') as writeFile:
    csvWriter = csv.writer(writeFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(["comma","colon","semicolon","dash","none"])
    finalCount = [0,0,0,0,0]
    with open(file + ".csv", newline='') as readFile:
        csvReader = csv.reader(readFile, delimiter=',', quotechar='"')
        # skip first line
        next(csvReader, None)
        for row in csvReader:
            contains = False
            tempCount = ["","","","",""]
            if "," in str(row[0]):
                tempCount[0] = str(row[1])
                finalCount[0] += 1
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
            if not contains:
                tempCount[4] = str(row[1])
                finalCount[4] += 1    
            csvWriter.writerow(tempCount)
        csvWriter.writerow(finalCount)