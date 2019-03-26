import numpy as np
import pandas as pd
from skmultilearn.problem_transform import ClassifierChain
import os
import ast
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.naive_bayes import GaussianNB
import sklearn.metrics
from collections import *

class TrainModel:
    def __init__(self, folds_dir, feat_file):
        self.folds_dir = folds_dir
        self.features_file = feat_file

        self.feat_type = [['disease_tfidf'], ['symptoms_tfidf'], ['medications_tfidf'],
                          ['disease_tfidf','symptoms_tfidf','medications_tfidf']]

        self.feat_dim = {}
        self.feat_dim['disease_tfidf'] = 1269 # This is for each feature
        self.feat_dim['symptoms_tfidf'] = 1374  # This is for each feature
        self.feat_dim['medications_tfidf'] = 1248  # This is for each feature

        self.feat_dim_array = [1269, 1374, 1248, 3891]
        self.num_lab = 3 # This is dimension of labels - MULTI LABEL CLASSIFICATION

    def train(self):
        folds_count = 5

        feat_df = pd.read_pickle(self.features_file + '/' + 'EHR_tags_tfidf.pickle')

        avg_macro = defaultdict(int)
        avg_micro = defaultdict(int)
        avg_wt = defaultdict(int)

        for fold in range(1, folds_count+1):
            print('---------- Fold no. {} -----------'.format(fold))
            tr_lab_df = pd.read_csv(self.folds_dir + '/' + 'Train_fold_' + str(fold) + '.csv')
            te_lab_df = pd.read_csv(self.folds_dir + '/' + 'Test_fold_' + str(fold) + '.csv')

            # tr_lab_df = feat_df[feat_df['id'].isin(tr_lab['id'].tolist())]
            # te_lab_df = feat_df[feat_df['id'].isin(te_lab['id'].tolist())]

            for feat_id in range(len(self.feat_type)):
                features = self.feat_type[feat_id]
                X_tr = np.zeros((tr_lab_df.shape[0], self.feat_dim_array[feat_id]))
                Y_tr = np.zeros((tr_lab_df.shape[0], self.num_lab))

                X_te = np.zeros((te_lab_df.shape[0], self.feat_dim_array[feat_id]))
                Y_te = np.zeros((te_lab_df.shape[0], self.num_lab))

                start=0
                for f_id in range(len(features)):
                    feat = features[f_id]

                    ''' Iterate the features Dataframe'''
                    for idx, row in tr_lab_df.iterrows():
                        ehr_id = row['id']
                        feat_row = feat_df[feat_df['id'] == ehr_id] # Features row

                        if len(feat_row[feat]) > 0:
                            X_tr[idx][start:start+self.feat_dim[feat]] = np.array(feat_row[feat].iloc[0])
                        Y_tr[idx][:] = np.array([row['Diabetes'], row['Hypertension'], row['Obesity']])

                    for idx, row in te_lab_df.iterrows():
                        ehr_id = row['id']
                        feat_row = feat_df[feat_df['id'] == ehr_id] # Features row

                        if len(feat_row[feat]) > 0:
                            X_te[idx][start:start+self.feat_dim[feat]] = np.array(feat_row[feat].iloc[0])
                        Y_te[idx][:] = np.array([row['Diabetes'], row['Hypertension'], row['Obesity']])

                    start += self.feat_dim[feat]


                ''' Run the model '''
                classifier = ClassifierChain(GaussianNB())

                # train
                classifier.fit(X_tr, Y_tr)

                # predict
                Y_pr = classifier.predict(X_te).toarray()
                # print(predictions.toarray())

                hamming_sum = 0
                for inst in range(Y_te.shape[0]):
                    hamming_sum += sklearn.metrics.hamming_loss(Y_te[inst, :], Y_pr[inst, :])

                # print(hamming_sum / Y_te.shape[0])

                avg_macro[feat_id] += sklearn.metrics.recall_score(Y_te, Y_pr, average='macro')
                avg_micro[feat_id] += sklearn.metrics.recall_score(Y_te, Y_pr, average='micro')
                avg_wt[feat_id] += sklearn.metrics.recall_score(Y_te, Y_pr, average='weighted')

        for feat_id in range(len(self.feat_type)):
            features = self.feat_type[feat_id]
            print("-------- Features: {} ---------".format(features))

            print("Micro: ", avg_micro[feat_id]/5)
            print("Macro: ", avg_macro[feat_id]/5)
            print("Weighted: ", avg_wt[feat_id]/5)






