from _DB_Connection.db_connection import *
import os

if __name__ == '__main__':

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    ehr = ""
    numberCategories = 10

    numberEHRs = len(os.listdir("./input_files")) / numberCategories
    categories = ['pri','sec','his','pre','pas','fam','soc','all','adm','dis']

    for id in range(numberEHRs):

        print str(id + 1) + " out of " + str(numberEHRs)

        for cat in categories:

            line = open("./input_files/ehr_" + format(int(id),'03d') + "_" + cat,"r")
            ehr += line.readline() + " "

        saveOriginalEHR(con,cur, id, ehr.strip(), -1)

        ehr = ""