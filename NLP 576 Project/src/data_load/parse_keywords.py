__author__ = 'DarkWeb'

import glob
import os
import codecs

from _DB_Connection.db_connection import *
from bs4 import BeautifulSoup

def parse_html(feature):

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    lines = []
    soup = ""

    for fileListing in glob.glob(os.path.join ("./medical_dictionary/HTML_Pages" ,'*.html')):
        lines.append(fileListing)

    for index, line in enumerate(lines):

        readError = False
        try:
            html = codecs.open(line.strip('\n'), encoding='utf8')
            soup = BeautifulSoup(html, "html.parser")
        except:
            try:
                html = open(line.strip('\n'))
                soup = BeautifulSoup(html, "html.parser")
            except:
                print ("There was a problem to read the file " + line + " in the listing section!")
                readError = True

        if not readError:

           items = soup.find('div', {"id": "results-area"}).find('div', {"class": "words"}).findAll('a', {"class": "item"})

           for i, item in enumerate(items):

               print str(i+1) + " out of " + str(len(items))

               save_keyword(cur, con, feature, item.text)

""" This is a script to test the Parser """

if __name__ == '__main__':

    parse_html(feature='bmi')

    print "Process Finished!!!"