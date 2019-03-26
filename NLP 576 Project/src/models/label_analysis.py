import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import re

class Labels:
    def __init__(self, ):
        '''

        :param inpPath: Input to the ground truth
        '''

        # self.file_path = inpPath  # Comment out so that multiple files can be used for filling doc_lab_map
        self.doc_lab_map = {} # user -> set(diseases)
        self.document_count = 0
        self.phenotypes = ['Asthma', 'CAD', 'CHF', 'Depression', 'Diabetes',
                           'Gallstones', 'GERD', 'Gout', 'Hypercholesterolemia',
                           'Hypertension', 'Hypertriglyceridemia', 	'OA', 'Obesity',
                           'OSA', 	'PVD', 'Venous Insufficiency']  # also referred to as diseases
        self.corr_mat = np.zeros((len(self.phenotypes), len(self.phenotypes)))


    def label_distribution(self):
        '''
        The objective is to plot the correlation matrix for the  phenotypes
        Select 3/4 phenotypes for classification - based on empiricial evidence
        from the correlation matix

        :return:
        '''

        for p_i in range(len(self.phenotypes)):
            for p_j in range(len(self.phenotypes)):
                ph_pair = [self.phenotypes[p_i], self.phenotypes[p_j]]

                for uid in self.doc_lab_map:
                    # print(uid, ph_pair, self.doc_lab_map[uid], all(x in self.doc_lab_map[uid] for x in ph_pair))
                    if all(x in self.doc_lab_map[uid] for x in ph_pair):
                        self.corr_mat[p_i][p_j] += 1

        return self.corr_mat, self.phenotypes

    def doc_parse(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        '''
        The current label record in the data is stored with this hierarchy:
                diseaseset
                  '
                  '---> diseases
                          '
                          '---> disease --->  Asthma/Obesity/......

        Each record of a patient is structured within the doc nodes.
        Each EHR record can be stored in a different format -- this script might need to be
        edited in this method to cater to different EHR formats

        '''
        for child in root:
            if child.tag == 'diseases':
                break
        count = 0
        for l in child:
            # print(l.tag, l.attrib['name'])
            disease = l.attrib['name']
            count += 1

            for doc in l:
                docid = int(doc.attrib['id'])
                if docid not in self.doc_lab_map:
                    self.doc_lab_map[docid] = []

                if doc.attrib['judgment'] == 'Y':
                    self.doc_lab_map[docid].append(disease)

    def save_file(self):
        columns = ['id']
        columns.extend(self.phenotypes)
        df = pd.DataFrame(columns=columns )

        for id in self.doc_lab_map:
            val_list = [id]
            for ph in range(len(self.phenotypes)):
                if self.phenotypes[ph] in self.doc_lab_map[id]:
                    val_list.append(1)
                else:
                    val_list.append(0)

            df.loc[id] = val_list

            # df.to_csv(self.outputPath + 'EHR_records_' + mode + '.csv')
        return df



