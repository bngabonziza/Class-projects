"""
Description     : Simple Python implementation of the Apriori Algorithm to train our model an generate rules
"""

from _DB_Connection.db_connection import *
from itertools import chain, combinations
from collections import defaultdict
from testing import testing

def hasDisease(item, diseases):

    if len(item.intersection(diseases)) > 0:
       return True
    else:
       return False

def isDisease(item, diseases):

    if item.issubset(diseases):
       return True
    else:
       return False

def pruneRules(rules):

    pruned_rules = {}

    for rule in rules:

        if pruned_rules.has_key(rule[0][0]):
           if rule[2] > pruned_rules[rule[0][0]][2]:
              pruned_rules[rule[0]] = (rule[0],rule[1],rule[2])
        else:
           pruned_rules[rule[0][0]] = (rule[0],rule[1],rule[2])

    return pruned_rules.values()

def sortRules(rules):

    sorted_rules = sorted(rules, key=lambda confidence: confidence[2], reverse=True)

    return sorted_rules

def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """calculates the support for items in the itemSet and returns a subset
       of the itemSet each of whose elements satisfies the minimum support"""
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in localSet.items():
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


def runApriori(data_iter, diseases, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in largeSet.items()[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:

                if not hasDisease(element, diseases):

                    remain = item.difference(element)

                    if len(remain) > 0 and isDisease(remain, diseases):
                        confidence = getSupport(item)/getSupport(element)
                        if confidence >= minConfidence:
                            toRetRules.append(((tuple(element), tuple(remain)),getSupport(item),
                                               confidence))

    return toRetItems, toRetRules


def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    for item, support in sorted(items, key=lambda (item, support): support):
        print "item: %s , %.3f" % (str(item), support)
    print "\n------------------------ RULES:"
    for rule, confidence in sorted(rules, key=lambda (rule, confidence): confidence):
        pre, post = rule
        print "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence)

def cleanText(values):

   values = values.replace("[","")
   values = values.replace("]","")
   values = values.replace("'","")
   values = values.replace(" ","")

   return values

def getData(file_iter):

    """Function which reads from the file and yields a generator"""

    record = []

    for line in file_iter:
            record.append(frozenset(cleanText(line.__str__()).split(',')))

    return record

if __name__ == "__main__":

    #Connecting to the database
    con = connectDataBase()
    cur = con.cursor()

    diseases = frozenset({'Diabetes','Hypertension','Obesity'})
    supportcount = 25
    minConfidence = 0.6

    pMacroFinal = 0
    pMicroFinal = 0
    pWeightedFinal = 0
    rMacroFinal = 0
    rMicroFinal = 0
    rWeightedFinal = 0
    f1MacroFinal = 0
    f1MicroFinal = 0
    f1WeightedFinal = 0

    for fold in range(1,6):

        deleteRules(cur, con)

        inFile = getData(getRiskFactors(cur, fold))

        print "Len: " + str(len(inFile))

        minSupport = supportcount / (len(inFile) + 0.0)

        items, rules = runApriori(inFile, diseases, minSupport, minConfidence)

        rules = pruneRules(rules)
        rules = sortRules(rules)

        saveRules(cur, con, rules)

        p_macro, p_micro, p_weighted, r_macro, r_micro, r_weighted, f1_macro, f1_micro, f1_weighted = testing(fold, randomAssignment = False)

        pMacroFinal += p_macro
        pMicroFinal += p_micro
        pWeightedFinal += p_weighted

        rMacroFinal += r_macro
        rMicroFinal += r_micro
        rWeightedFinal += r_weighted

        f1MacroFinal += f1_macro
        f1MicroFinal += f1_micro
        f1WeightedFinal += f1_weighted

        print "********************************"

    print "p_score macro: " + str(pMacroFinal/5)
    print "p_score micro: " + str(pMicroFinal/5)
    print "p_score weighted: " + str(pWeightedFinal/5)

    print "r_score macro: " + str(rMacroFinal/5)
    print "r_score micro: " + str(rMicroFinal/5)
    print "r_score weighted: " + str(rWeightedFinal/5)

    print "f1_score macro: " + str(f1MacroFinal/5)
    print "f1_score micro: " + str(f1MicroFinal/5)
    print "f1_score weighted: " + str(f1WeightedFinal/5)