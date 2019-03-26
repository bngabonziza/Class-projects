__author__ = 'DarkWeb'

import psycopg2
import traceback

def connectDataBase():

    try:

        return psycopg2.connect(host='EN4109641', user='postgres', password='Impossible2', dbname='medical')

    except:

        print ("Data base (medical) not found.")
        raise SystemExit

def getLastMarketPlace(cur, con):

    try:

        cur.execute("select id_mk from marketPlaces order by id_mk desc limit 1")

        recset = cur.fetchall()

        if recset:
            return recset[0][0]
        else:
            return 0

    except:

        trace = traceback.format_exc()
        print (trace)

def getEHRCategory(cur, shortNameCategory):

    try:

        cur.execute("select category_id from ehrs_categories where description like '" + shortNameCategory + "%'")

        recset = cur.fetchall()

        if recset:
            return recset[0][0]
        else:
            return 0

    except:

        trace = traceback.format_exc()
        print (trace)

def getEHRTag(cur, nameTag):

    try:

        cur.execute("select id from tags where description = %(nameTag)s ", {'nameTag': nameTag})

        recset = cur.fetchall()

        if recset:
            return recset[0][0]
        else:
            return 0

    except:

        trace = traceback.format_exc()
        print (trace)

def getSentenceNumber(cur, ehr_id, category_id, begin, end):

    try:

        cur.execute("select sentence_id from records_sentences where ehr_id = %(ehr_id)s and category_id = %(category_id)s and "
                    "begin <= %(begin)s and \"end\">=%(end)s", {'ehr_id': ehr_id, 'category_id': category_id, 'begin': begin, 'end': end})

        recset = cur.fetchall()

        if recset:
            return recset[0][0]
        else:
            return 0

    except:

        trace = traceback.format_exc()
        print (trace)

def getData(cur):

    # Test
    dicRisks = {}

    # dicTopics[1] = ['Producto1','Producto2','Producto5']
    # dicTopics[2] = ['Producto1','Producto2','Producto4']
    # dicTopics[3] = ['Producto1','Producto2','Producto3','Producto5']
    # dicTopics[4] = ['Producto2','Producto4']
    # dicTopics[5] = ['Producto1','Producto3']
    # dicTopics[6] = ['Producto2','Producto3']
    # dicTopics[7] = ['Producto1','Producto2','Producto3']
    # dicTopics[8] = ['Producto1','Producto3']
    # dicTopics[9] = ['Producto2','Producto3']

    # dicTopics[1] = ['apple','beer','rice','chicken']
    # dicTopics[2] = ['apple','beer','rice']
    # dicTopics[3] = ['apple','beer']
    # dicTopics[4] = ['apple','mango']
    # dicTopics[5] = ['milk','beer','rice','chicken']
    # dicTopics[5] = ['beer','rice','chicken']
    # dicTopics[6] = ['milk','beer']
    # dicTopics[7] = ['milk','mango']

    dicRisks[1] = ['bmi','htn']
    dicRisks[2] = ['bmi','htn','trigl']
    dicRisks[3] = ['bmi','trigl']
    dicRisks[4] = ['triglt','tchol']

    return dicRisks.values()

def saveOriginalEHR(con, cur, id, description, label):

    try:

        sql = "Insert into records (id, description, label) values (%s, %s, %s)"
        recset = [id, description, label]
        cur.execute(sql, recset)

        con.commit()

    except:

        con.rollback()

        print ("There was a problem while saving the original EHR." )
        raise SystemExit

def saveSentenceEHR(con, cur, ehr_id, category_id, sentence_id, begin, end, content):

    try:

        sql = "Insert into records_sentences (ehr_id, category_id, sentence_id, begin, \"end\", content) values (%s, %s, %s, %s, %s, %s)"
        recset = [ehr_id, category_id, sentence_id, begin, end, content]
        cur.execute(sql, recset)

        con.commit()

    except:

        con.rollback()

        print ("There was a problem while saving one of the EHR sentences." )
        raise SystemExit

def saveTagEHR(con, cur, ehr_id, category_id, sentence_id, tag_id, begin, end, content, polarity, ontologyConceptArr):

    try:

        sql = "Insert into records_sentences_tags (ehr_id, category_id, sentence_id, tag_id, begin, \"end\", content, polarity, ontologyConceptArr) " \
              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        recset = [ehr_id, category_id, sentence_id, tag_id, begin, end, content, polarity, ontologyConceptArr]
        cur.execute(sql, recset)

        con.commit()

    except:

        con.rollback()

        print ("There was a problem while saving one of the cTakes tags." )
        raise SystemExit

def saveTagUMLS(con, cur, ehr_id, category_id, code, cui, tui, codingScheme, preferredText):

    try:

        sql = "Insert into records_umls (ehr_id, category_id, code, cui, tui, codingScheme, preferredText) " \
              "values (%s, %s, %s, %s, %s, %s, %s)"
        recset = [ehr_id, category_id, code, cui, tui, codingScheme, preferredText]
        cur.execute(sql, recset)

        con.commit()

    except:

        con.rollback()

        print ("There was a problem while saving one of the cTakes UMLS tags." )
        raise SystemExit

def saveRules(cur, con, forum_id, rules, minsupport, supportcount):

    sorted_rules = sorted(rules, key=lambda confidence: confidence[2], reverse=True)

    for rule, support, confidence in sorted_rules:

        pre, post = rule

        sizeAntecedent = len(pre)
        sizeConsequent = len(post)

        pre = pre.__str__().replace(")","")
        pre = pre.replace("(","")
        pre = pre.replace("'","")

        if pre[-1] == ",":
           pre = pre[0:len(pre)-1]

        post = post.__str__().replace(")","")
        post = post.replace("(","")
        post = post.replace("'","")

        if post[-1] == ",":
           post = post[0:len(post)-1]

        print "Rule: %s ==> %s , %.3f, %.3f" % (str(pre), str(post), support ,confidence)

        #sQL = "Insert into rules (forum_id, antecedent, consequent, supportcount, minsupport, confidence, sizeantecedent,"
        #sQL += "sizeconsequent) Values (%s, %s, %s, %s, %s, %s, %s, %s)"

        #recset = [forum_id, pre, post, supportcount, '{0:.3f}'.format(minsupport), '{0:.3f}'.format(confidence),
        #          sizeAntecedent, sizeConsequent]

        #cur.execute(sQL, recset)

        #con.commit()