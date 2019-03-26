import numpy as np
import pandas
import pickle
import xml.etree.ElementTree as ET
import re
import pandas as pd
''' To parse, xml library has been used - Beautiful Soup can also be used if you like it'''


class EHR_Parse:
    def __init__(self, fpath, outPath='../data/outputs/EHR/'):
        self.file_path = fpath
        self.outputPath = outPath
        self.ehr_records = {} # KEY: id of ehr # VALUE: Dictionary of different sections
        self.ehr_tags = ['PRIMARY DIAGNOSIS',
                         'SECONDARY DIAGNOSIS', 'HISTORY OF PRESENT ILLNESS',
                         'PRE-ADMISSION MEDICATIONS', 'PAST MEDICAL HISTORY', 'FAMILY HISTORY',
                         'SOCIAL HISTORY', 'ALLERGIES',
                         'PHYSICAL EXAMINATION',
                         'DISCHARGE MEDICATIONS'] # These tags can be more exhaustive

        self.ehr_tags_subst = ['PRINCIPAL DIAGNOSES',  'PRIMARY DIAGNOSES', 'PRINCIPAL DIAGNOSIS',
                               'PRINCIPAL DIAGNOSIS FOR ADMISSION', 'OTHER DIAGNOSIS', 'OTHER DIAGNOSES', 'SECONDARY DIAGNOSES',
                               'PRIMARY DIAGNOSIS ON ADMISSION', 'PRE-ADMISSION MEDS'
                         'ADMISSION PHYSICAL EXAMINATION', 'ADMISSION  ON PHYSICAL EXAMINATION',
                               'PHYSICAL EXAMINATION ON ADMISSION', 'MEDICATIONS', 'HOME MEDICATIONS', 'DISCHARGE MEDICATIONS WERE']

        # self.ehr_tags = ['HISTORY OF PRESENT ILLNESS', 'SOCIAL HISTORY', 'DISCHARGE MEDICATIONS']  # These tags can be more exhaustive
        self.docNumber = 0
        self.ehr_id_map = {}

    def splitRecord(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        '''
        The current EHR record in the data is stored with this hierarchy:
                root
                  '
                  '---> docs
                          '
                          '---> doc

        Each record of a patient is structured within the doc nodes.
        Each EHR record can be stored in a different format -- this script might need to be
        edited in this method to cater to different EHR formats

        '''
        for child in root:
            if child.tag == 'docs':
                break

        ''' Start processing each record from here'''
        for ehr_rec in child:
            print('Processing document ID: ', self.docNumber)
            # print(ehr_rec.attrib['id'])
            self.ehr_id_map[self.docNumber]  = ehr_rec.attrib['id']
            # docid = int(ehr_rec.attrib['id'])
            self.ehr_records[self.docNumber] = {}

            for child in ehr_rec: # This is where the text is stored
                ehr_text = child.text

                '''
                ALL THE TAGS IN THIS DOCUMENT ARE CAPITAL CASED FOLLOWED BY THE CHARACTER ':'

                SPLIT BY THE REGEX EXP that abstracts this pattern - <TEXT in CAPS>: which returns the tags

                THIS WOULD PREVENT DATES AS TAGS e.g. 8:30 would not be matched OR q: will not be considered a atg
                '''

                lines = ehr_text.split('\n') # Split the raw text by lines
                lnumber = 0
                ehr_tag_text = ''
                last_tag = ''
                start_collect = 0 # This is flag to start of ehr text track

                while lnumber < len(lines):
                    ltext = lines[lnumber]

                    '''
                    This is a trivial regular expression - Can be made more robust like

                    [A-Z]?[\s\-]?[A-Z]+:

                    '''
                    ltag = re.findall('[a-zA-Z\s\-]+[:;]+', ltext)

                    if len(ltag) > 0:
                        ltag = ltag[0][:-1] # -1 for removing ':'
                        ''' First save the previous tag text '''

                        if len(ehr_tag_text) > 0:
                            self.ehr_records[self.docNumber][last_tag] = ehr_tag_text
                            ehr_tag_text = ''  # Reset for next tag

                        ltag = ltag.split('.')
                        ltag = (ltag[-1:][0]).lstrip()

                        '''
                        If the tag in the current line is required, start collecting the text
                        until the next tag (whatever) is found. Else, do not collect the data
                        until the next relevant tag is found.
                        '''

                        if ltag in self.ehr_tags or ltag in self.ehr_tags_subst:
                            start_collect = 1

                            ''' Split the line by either ; or : '''

                            try:
                                phrases = lines[lnumber].split(':')
                                text_tag = phrases[1][1:]
                                text_tag = text_tag.split('.')
                                ehr_tag_text += text_tag[0] + ' '
                            except:
                                phrases = lines[lnumber].split(';')
                                text_tag = phrases[1]
                                text_tag = text_tag.split('.')
                                ehr_tag_text += text_tag[0] + ' '

                            if ltag == 'PRINCIPAL DIAGNOSIS' or ltag == 'PRINCIPAL DIAGNOSIS FOR ADMISSION' or ltag == 'PRIMARY DIAGNOSES' or ltag == 'PRINCIPAL DIAGNOSES' \
                                or ltag == 'PRIMARY DIAGNOSIS ON ADMISSION':
                                ltag = 'PRIMARY DIAGNOSIS'
                            if ltag == 'OTHER DIAGNOSES' or ltag == 'OTHER DIAGNOSIS' or ltag == 'SECONDARY DIAGNOSES':
                                ltag = 'SECONDARY DIAGNOSIS'
                            if ltag == 'MEDICATIONS' or ltag == 'HOME MEDICATIONS' or ltag == 'PRE-ADMISSION MEDS':
                                ltag = 'PRE-ADMISSION MEDICATIONS'
                            if ltag == 'ADMISSION PHYSICAL EXAMINATION' or ltag == 'ADMISSION ON PHYSICAL EXAMINATION' \
                                or ltag == 'PHYSICAL EXAMINATION ON ADMISSION':
                                ltag = 'PHYSICAL EXAMINATION'
                            # elif ltag in 'PHYSICAL EXAMINATION ON ADMISSION':
                            #     ltag = 'ADMISSION PHYSICAL EXAMINATION'
                            last_tag = ltag
                        else:
                            start_collect = 0
                    else:
                        if start_collect:
                            ehr_tag_text += lines[lnumber] + ' '
                    lnumber += 1

            self.docNumber += 1

    def saveFile(self, mode='train'):
        '''

        :return:
        '''
        # pickle.dump(self.ehr_records, open(self.outputPath + 'EHR_records_dict_' + mode + '.pickle', 'wb'))

        columns = ['id']
        columns.extend(self.ehr_tags)
        df = pd.DataFrame(columns=columns )
        for id in range(self.docNumber):
            val_list = [self.ehr_id_map[id]]
            for tidx in range(len(self.ehr_tags)):
                try:
                    val_list.append(self.ehr_records[id][self.ehr_tags[tidx]])
                except:
                    val_list.append('')

            df.loc[id] = val_list

        # df.to_csv(self.outputPath + 'EHR_records_' + mode + '.csv')
        return df















