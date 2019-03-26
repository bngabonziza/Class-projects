from _DB_Connection.db_connection import *

if __name__ == '__main__':

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    updateLabels(cur, con)

    print "Process finished!"