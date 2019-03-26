from _DB_Connection.db_connection import *
import os
import re

def tagParser(cur, lineXMI, ehr_id, cat, regExpression, tag):

    regex = regExpression
    match = re.search(regex, lineXMI)

    if match != None:
       string = lineXMI[match.start():match.end()]
       records = string.split("/>")

       for record in records:

           if record.__contains__(tag):

                regex = r"codingScheme=\"\w+\""
                match = re.search(regex, record)
                codingScheme = match.string[match.start():match.end()]
                codingScheme = codingScheme.replace("codingScheme=","")
                codingScheme = str(codingScheme.replace("\"",""))

                regex = r"code=\"\d+\""
                match = re.search(regex, record)

                if match != None:
                   code = match.string[match.start():match.end()]
                   code = code.replace("code=","")
                   code = int(code.replace("\"",""))
                else:
                   code = None

                regex = r"cui=\"\w+\""
                match = re.search(regex, record)
                cui = match.string[match.start():match.end()]
                cui = cui.replace("cui=","")
                cui = str(cui.replace("\"",""))

                regex = r"tui=\"\w+\""
                match = re.search(regex, record)
                tui = match.string[match.start():match.end()]
                tui = tui.replace("tui=","")
                tui = str(tui.replace("\"",""))

                regex = r"preferredText=\".+\""
                match = re.search(regex, record)

                if match != None:
                   preferredText = match.string[match.start():match.end()]
                   preferredText = preferredText.replace("preferredText=","")
                   preferredText = str(preferredText.replace("\"",""))
                else:
                   preferredText = None

                category = getEHRCategory(cur, cat)

                saveTagUMLS(con, cur, ehr_id, category, code, cui, tui, codingScheme, preferredText)

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

            tagParser(cur, lineXMI, ehr_id, cat, r"(<refsem:UmlsConcept).+(preferredText=\".+\"/>)", "UmlsConcept")