from _DB_Connection.db_connection import *

if __name__ == '__main__':

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    dicAge = getAge(cur)
    dicGender = getGender(cur)
    dicBMI = getBMI(cur)
    dicSBP, dicDBP = getBP(cur)
    dicChol = getCholesterol(cur)
    dicTrigl = getTriglycerides(cur)
    dicLabels = getLabels(cur)

    saveFeatures(cur, con, dicAge, dicGender, dicBMI, dicSBP, dicDBP, dicChol, dicTrigl, dicLabels)

    print "Process finished!"