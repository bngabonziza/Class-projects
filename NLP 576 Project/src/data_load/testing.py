"""
Description     : Simple Python implementation of the testing cases
"""

import numpy as np
from sklearn.metrics.classification import precision_score, recall_score, f1_score

from _DB_Connection.db_connection import *
import random

def testing(fold, randomAssignment = False):

    try:

        #Connecting to the database
        con = connectDataBase()
        cur = con.cursor()

        labels = []
        pred = []

        rules = getRules(cur)

        testCases = getTestCases(cur, fold)

        for i, testcase in enumerate(testCases):

            if "Diabetes" in testcase[8]:
               diabetes = 1
            else:
               diabetes = 0

            if "Hypertension" in testcase[8]:
               hypertension = 1
            else:
               hypertension = 0

            if "Obesity" in testcase[8]:
               obesity = 1
            else:
               obesity = 0

            labels.append([diabetes,hypertension,obesity])

            if randomAssignment:

                diabetes = random.randint(0, 1)
                hypertension = random.randint(0, 1)
                obesity = random.randint(0, 1)

            else:

                testCovered = False
                riskFactors = []
                ruleClassifier = ()

                for rule in rules:

                    if testcase[1] != None:
                       riskFactors.append(testcase[1])
                    if testcase[2] != None:
                       riskFactors.append(testcase[2])
                    if testcase[3] != None:
                       riskFactors.append(testcase[3])
                    if testcase[4] != None:
                       riskFactors.append(testcase[4])
                    if testcase[5] != None:
                       riskFactors.append(testcase[5])
                    if testcase[6] != None:
                       riskFactors.append(testcase[6])
                    if testcase[7] != None:
                       riskFactors.append(testcase[7])

                    bRule = True
                    for riskFactor in riskFactors:

                        if not rule.__str__().__contains__(riskFactor):
                           bRule = False
                           break

                    if bRule:
                       testCovered = True
                       ruleClassifier = rule
                       break

                if testCovered:

                    if "Diabetes" in ruleClassifier[2]:
                       diabetes = 1
                    else:
                       diabetes = 0

                    if "Hypertension" in ruleClassifier[2]:
                       hypertension = 1
                    else:
                       hypertension = 0

                    if "Obesity" in ruleClassifier[2]:
                       obesity = 1
                    else:
                       obesity = 0

                else:

                    diabetes = 1
                    hypertension = 1
                    obesity = 1

            pred.append([diabetes,hypertension,obesity])

        y_true = np.array(labels)
        y_pred = np.array(pred)

        #print "f1_score macro: " + str(f1_score(y_true=y_true, y_pred=y_pred, average='macro'))
        #print "f1_score micro: " + str(f1_score(y_true=y_true, y_pred=y_pred, average='micro'))
        #print "f1_score weighted: " + str(f1_score(y_true=y_true, y_pred=y_pred, average='weighted'))


        return precision_score(y_true=y_true, y_pred=y_pred, average='macro'), recall_score(y_true=y_true, y_pred=y_pred, average='macro'),\
               f1_score(y_true=y_true, y_pred=y_pred, average='macro'), precision_score(y_true=y_true, y_pred=y_pred, average='micro'), \
               recall_score(y_true=y_true, y_pred=y_pred, average='micro'), f1_score(y_true=y_true, y_pred=y_pred, average='macro'),\
               precision_score(y_true=y_true, y_pred=y_pred, average='weighted'), recall_score(y_true=y_true, y_pred=y_pred, average='weighted'),\
               f1_score(y_true=y_true, y_pred=y_pred, average='weighted')

    except:

        trace = traceback.format_exc()
        print (trace)