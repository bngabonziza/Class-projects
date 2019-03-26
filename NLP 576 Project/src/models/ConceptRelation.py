import numpy as np
import pandas as pd
import psycopg2
from collections import *
import matplotlib.pyplot as plt
from nltk.corpus import wordnet


class Med_Knowledge_Graph:
    def __init__(self, ):
        '''

        :param inpPath: Input to the ground truth
        '''

        # self.file_path = inpPath  # Comment out so that multiple files can be used for filling doc_lab_map
        self.phenotypes = ['Asthma', 'CAD', 'CHF', 'Depression', 'Diabetes',
                           'Gallstones', 'GERD', 'Gout', 'Hypercholesterolemia',
                           'Hypertension', 'Hypertriglyceridemia', 	'OA', 'Obesity',
                           'OSA', 	'PVD', 'Venous Insufficiency']  # also referred to as diseases

        self.symptoms_stop = ['normal', 'history', 'mild', 'signs', 'rest', 'test', 'football', 'never married',
                              'rested', 'work', 'feeling better', 'much better', ]

        self.disease_stop = ['disease']

        self.cause_synonyms = ['causes', 'leads', 'results', 'produce', 'caused', 'lead', 'causing', 'gets',
                               'gives', 'makes', 'leading', 'resulting']

        synonyms = []
        for syn in wordnet.synsets("cause"):
            for l in syn.lemmas():
                synonyms.append(l.name())

        self.cause_synonyms.extend(list(set(synonyms)))
        self.cause_synonyms = list(set(self.cause_synonyms))

        ''' STORE THE TAG ASSOCIATION TUPLES '''
        self.sym_r_sym = [] # Pairs for symptom --> symptoms
        self.med_de_symp = [] # Pairs for symptom --> symptoms
        self.sym_c_dis = [] # Pairs for symptom --> symptoms
        self.med_de_dis = [] # Pairs for symptom --> symptoms


    def getDatabaseConcepts(self):
        ''' Create the connection and form the mappings '''

        host = '10.218.109.4'
        database = 'medical'
        user='postgres'
        passw = 'Impossible2'
        conn_str = "host={} dbname={} user={} password={}".format(host, database, user, passw)

        conn = psycopg2.connect(conn_str)

        # 1. Tags
        df = pd.read_sql('select * from tags', con=conn)
        self.tag_id_map = pd.Series(df.description.values,index=df.id).to_dict() # Map columns to dictionaries

        # 2. EHR Categories
        df = pd.read_sql('select * from ehrs_categories', con=conn)
        self.ehrCat_id_map = pd.Series(df.description.values, index=df.category_id).to_dict()  # Map columns to dictionaries

        # 3. EHR -> Category --> Sentence --> Content
        self.sentences_tags_map = pd.read_sql('select * from records_sentences_tags', con=conn)

        # 4. EHR --> Category --> Sentences
        self.sentences_records_map = pd.read_sql('select * from records_sentences', con=conn)


    def getDistTags(self):
        '''
        Check the distribution of the tags

        :return:
        '''
        self.dis_count = defaultdict(int)
        for idx, row in self.sentences_tags_map.iterrows():
            phrase = row['content']
            if row['tag_id'] == 3 and row['polarity'] == 1: # Disease Disorder mention
                self.dis_count[phrase] += 1

        for dis in self.dis_count:
            if self.dis_count[dis] < 10:
                print(dis, self.dis_count[dis])


    def associateTags(self):
        '''
        The following just mimics the groupby operation to reach the sentence level grouped by
        all the other attributes like ehr_id, category_id ,,,,

        TODO: only consider few scetions for EHR for constructing the knowledge graphg=
        :return:
        '''
        ehrCount = 0
        ehr_ids = list(set(self.sentences_tags_map['ehr_id']))


        ''' EHR/PATIENT LEVEL '''
        for eid in ehr_ids:
            print("\n Processing EHR ID: ", eid)
            ehr = self.sentences_tags_map[self.sentences_tags_map['ehr_id'] == eid ]

            cat_ids = list(set(ehr['category_id']))
            ''' EHR CATEGORY LEVEL '''
            for cid in cat_ids:

                sentences = ehr[ehr['category_id'] == cid]
                sent_ids = list(set(sentences['sentence_id']))


                ''' SENTENCE LEVEL '''
                for sid in sent_ids:
                    ''' Get the actual sentence from the EHR '''
                    sent = self.sentences_records_map[(self.sentences_records_map['ehr_id'] == eid) & (self.sentences_records_map['category_id'] == cid)
                                                     & (self.sentences_records_map['sentence_id'] == sid) ]

                    sent_ctakes = self.sentences_tags_map[
                        (self.sentences_tags_map['ehr_id'] == eid) & (self.sentences_tags_map['category_id'] == cid)
                        & (self.sentences_tags_map['sentence_id'] == sid)]

                    # print(self.ehrCat_id_map[cid], sid, sent.iloc[0]['content'])

                    ''' Get the word tags from the cTakes database '''
                    words_tag_ids = defaultdict()
                    for idx_s, row_s in sent_ctakes.iterrows():
                        words_tag_ids[row_s['content']] = row_s['tag_id']

                    ''' CONSIDER ALLERGIES HERE '''
                    if cid > 0: #== 8:
                        ''' 1. SPplit the sentence into words
                            2. Check if the word is tagged by cTakes
                        '''

                        content = (sent.iloc[0]['content']).lstrip()
                        content = content.rstrip()
                        if content[-1:] == '.':
                            content = content[:-1]

                        if len(content) == 0:
                            continue
                            # print(sent.iloc[0]['content'], len(content))

                        words = content.split(' ')

                        ''' Check if there are overlap between words and cause-synonyms'''
                        # print(list(set(self.cause_synonyms).intersection(set(words))))
                        contains_Cause = list(set(self.cause_synonyms).intersection(set(words)))
                        if len(contains_Cause) > 0:
                            symp_cause = []
                            dis_cause = []
                            med_cause = []

                            symp_effect = []
                            dis_effect = []
                            med_effect = []

                            w_id= 0

                            ''' Store all the tags till the 'cause'  '''
                            # print(words)
                            while words[w_id] not in self.cause_synonyms:
                                if words[w_id] in words_tag_ids:
                                    if words_tag_ids[words[w_id]] == 3: # symptoms
                                        symp_cause.append(words[w_id])
                                    if words_tag_ids[words[w_id]] == 1: # medication
                                        med_cause.append(words[w_id])
                                    if words_tag_ids[words[w_id]] == 2: # dis
                                        dis_cause.append(words[w_id])

                                w_id += 1

                            # print(symp_cause)
                            # print(dis_cause)
                            # print(med_cause)

                            # ''' Keep traversing to the end till get a disease'''
                            while w_id < len(words):
                                # if words[w_id] in words_tag_ids:
                                #     print(eid, cid, sid, words[w_id], self.tag_id_map[words_tag_ids[words[w_id]]])
                                if words[w_id] in words_tag_ids and words_tag_ids[words[w_id]] == 2: # disease
                                    dis_effect.append(words[w_id])
                                    break
                                if words[w_id] in words_tag_ids and words_tag_ids[words[w_id]] == 1:  # medication
                                    med_effect.append(words[w_id])
                                    break
                                if words[w_id] in words_tag_ids and words_tag_ids[words[w_id]] == 3:  # symptoms
                                    symp_effect.append(words[w_id])
                                    break

                                w_id += 1

                            # print(symp_effect)
                            # print(dis_effect)
                            # print(med_effect)

                            ''' Create the associations between the cause and effect
                                All of these links are associated with the 'CAUSE/LEADS TO' tags

                                1. Symptoms related to symptoms
                                2. Medicines drug_effects symptoms
                                3. Symptoms causes diseases
                                4. Medicines drug_effects diseases
                            '''

                            # 1.
                            for sc in symp_cause:
                                for se in symp_effect:
                                    print("sc, se", content, sc, se)
                                    self.sym_r_sym.append((sc, se))

                            # 2.
                            for sc in symp_cause:
                                for de in dis_effect:
                                    print("sc, de", content, sc, de)
                                    self.sym_c_dis.append((sc, de))

                            # 3.
                            for md in med_cause:
                                for se in symp_effect:
                                    print("md, se", content, md, se)
                                    self.med_de_symp.append((md, se))

                            # 4.
                            for md in med_cause:
                                for de in dis_effect:
                                    print("md, de", content, md, de)
                                    self.med_de_dis.append((md, de))

            ehrCount += 1
            # if ehrCount > 50:
            #     exit()

        print(len(self.med_de_dis), len(self.med_de_symp), len(self.sym_c_dis), len(self.sym_r_sym))
