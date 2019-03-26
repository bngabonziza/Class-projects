import numpy as np
import pandas as pd
from skmultilearn.problem_transform import ClassifierChain
import os
import ast
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.naive_bayes import GaussianNB
import sklearn.metrics


if __name__ == "__main__":

    hamming_sum = 0
    avg_micro = 0
    avg_macro = 0
    avg_wt = 0
    for fold in range(1, 5):
        X_tr_df = pd.read_csv('../../data/outputs/bernard/bernard_out/feature_train_tfidf' + str(fold) + '.csv')
        X_te_df = pd.read_csv('../../data/outputs/bernard/bernard_out/feature_test_tfidf' + str(fold) + '.csv')
        Y_tr_df = pd.read_csv('../../data/outputs/splits/Train_fold_' + str(fold) + '.csv')
        Y_te_df = pd.read_csv('../../data/outputs/splits/Test_fold_' + str(fold) + '.csv')

        X_tr = np.zeros((X_tr_df.shape[0], X_tr_df.shape[1]-1))
        Y_tr = np.zeros((X_tr_df.shape[0], 3))

        X_te = np.zeros((X_te_df.shape[0], X_te_df.shape[1]-1))
        Y_te_gt = np.zeros((X_te_df.shape[0], 3))

        count_row = 0
        for idx, row in X_tr_df.iterrows():
            X_tr[count_row, :] = list(row.iloc[1:])
            Y_tr[count_row, :] = list((Y_tr_df[Y_tr_df['id'] == row['id']]).iloc[0, 2:])

            count_row += 1

        count_row = 0
        for idx, row in X_te_df.iterrows():
            X_te[count_row, :] = list(row.iloc[1:])
            Y_te_gt[count_row, :] = list((Y_te_df[Y_te_df['id'] == row['id']]).iloc[0, 2:])

            count_row += 1

        ''' Run the model '''
        classifier = ClassifierChain(GaussianNB())

        # train
        classifier.fit(X_tr, Y_tr)

        # predict
        Y_pr = classifier.predict(X_te).toarray()
        # print(predictions.toarray())

        # for inst in range(Y_te.shape[0]):
        #     hamming_sum += sklearn.metrics.hamming_loss(Y_te[inst, :], Y_pr[inst, :])

        # print(hamming_sum / Y_te.shape[0])

        avg_macro += sklearn.metrics.f1_score(Y_te_gt, Y_pr, average='macro')
        avg_micro += sklearn.metrics.f1_score(Y_te_gt, Y_pr, average='micro')
        avg_wt += sklearn.metrics.f1_score(Y_te_gt, Y_pr, average='weighted')

    print("macro: ", avg_macro/5)
    print("micro: ", avg_micro/5)
    print("wt: ", avg_wt / 5)

