from _DB_Connection.db_connection import *
import os
import re

def tagParser(cur, lineXMI, lineEHR, ehr_id, cat, regExpression, tag):

    regex = regExpression
    match = re.search(regex, lineXMI)

    if match != None:
       string = lineXMI[match.start():match.end()]
       records = string.split("/>")

       for record in records:

           if record.__contains__(tag):
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

                regex = r"polarity=\"-?\d+\""
                match = re.search(regex, record)
                polarity = match.string[match.start():match.end()]
                polarity = polarity.replace("polarity=","")
                polarity = int(polarity.replace("\"",""))

                regex = r"ontologyConceptArr=\"(\d+\s?)+\""
                match = re.search(regex, record)
                ontologyConceptArr = match.string[match.start():match.end()]
                ontologyConceptArr = ontologyConceptArr.replace("ontologyConceptArr=","")
                ontologyConceptArr = str(ontologyConceptArr.replace("\"",""))

                category = getEHRCategory(cur, cat)

                sentenceNumber = getSentenceNumber(cur, ehr_id, category, begin, end)

                content = lineEHR[begin:end]

                saveTagEHR(con, cur, ehr_id, category, sentenceNumber, getEHRTag(cur, tag), begin, end, content, polarity, ontologyConceptArr)

           else:
              break

if __name__ == '__main__':

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    numberCategories = 10

    numberEHRs = len(os.listdir("./output_files")) / numberCategories
    categories = ['pri','sec','his','pre','pas','fam','soc','all','adm','dis']

    for ehr_id in range(numberEHRs):

        print str(ehr_id + 1) + " out of " + str(numberEHRs)

        for cat in categories:

            lineXMI = open("./output_files/ehr_" + format(int(ehr_id),'03d') + "_" + cat + ".xmi","r")
            lineXMI = lineXMI.readline().strip()

            lineEHR = open("./input_files/ehr_" + format(int(ehr_id),'03d') + "_" + cat,"r")
            lineEHR = lineEHR.readline().strip()

            tagParser(cur, lineXMI, lineEHR, ehr_id, cat, r"(<textsem:MedicationMention).+(historyOf=\"\d+\"/>)", "MedicationMention")

            tagParser(cur, lineXMI, lineEHR, ehr_id, cat, r"(<textsem:DiseaseDisorderMention).+(historyOf=\"\d+\"/>)", "DiseaseDisorderMention")

            tagParser(cur, lineXMI, lineEHR, ehr_id, cat, r"(<textsem:SignSymptomMention).+(historyOf=\"\d+\"/>)", "SignSymptomMention")

            tagParser(cur, lineXMI, lineEHR, ehr_id, cat, r"(<textsem:AnatomicalSiteMention).+(historyOf=\"\d+\"/>)", "AnatomicalSiteMention")

            tagParser(cur, lineXMI, lineEHR, ehr_id, cat, r"(<textsem:ProcedureMention).+(historyOf=\"\d+\"/>)", "ProcedureMention")




