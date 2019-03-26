from _DB_Connection.db_connection import *
import os
import re

if __name__ == '__main__':

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    ehr = ""
    numberCategories = 10

    numberEHRs = len(os.listdir("./output_files")) / numberCategories

    # for id in range(numberEHRs):
    #
    #     print str(id + 1) + " out of " + str(numberEHRs)
    #
    #     for cat in categories:
    #
    #         line = open("./input_files/ehr_" + format(int(id),'03d') + "_" + cat,"r")
    #         ehr += line.readline() + " "
    #
    #     saveOriginalEHR(con,cur, id, ehr.strip(), -1)
    #
    #     ehr = ""

    categories = ['pri','sec','his','pre','pas','fam','soc','all','adm','dis']

    for ehrID in range(numberEHRs):

        print str(ehrID + 1) + " out of " + str(numberEHRs)

        for cat in categories:

            lineXMI = open("./output_files/ehr_" + format(int(ehrID),'03d') + "_" + cat + ".xmi","r")
            lineXMI = lineXMI.readline().strip()

            lineEHR = open("./input_files/ehr_" + format(int(ehrID),'03d') + "_" + cat,"r")
            lineEHR = lineEHR.readline().strip()

            if len(lineEHR) > 0:

                sentenceNumber = 1

                regex = r"(<textspan:Sentence).+(sentenceNumber=\"\d+\"/>)"
                match = re.search(regex, lineXMI)

                string = lineXMI[match.start():match.end()]
                records = string.split("/>")

                for record in records:

                    regex = r"begin=\"\d+\""
                    match = re.search(regex, record)

                    if match != None:

                        begin = match.string[match.start():match.end()]
                        begin = begin.replace("begin=","")
                        begin = int(begin.replace("\"",""))

                        regex = r"end=\"\d+\""
                        match = re.search(regex, record)
                        end = match.string[match.start():match.end()]
                        end = end.replace("end=","")
                        end = int(end.replace("\"",""))

                        originalSentence = lineEHR[begin:end]

                        #saveSentenceEHR(con,cur, ehrID, getEHRCategory(cur, cat), sentenceNumber, begin, end, originalSentence)

                        sentenceNumber += 1

                        regex = r"(<textsemn:MedicationMention).+(sentenceNumber=\"\d+\"/>)"
                        match = re.search(regex, lineXMI)




