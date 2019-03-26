import pandas as pd
import numpy as np
import pickle
from sklearn import metrics
import scipy.stats as scst
from sklearn import linear_model
from sklearn import svm
from sklearn.model_selection import KFold
import sklearn.metrics
from sklearn.naive_bayes import GaussianNB
import random


def hamming_loss(Y_true, Y_predict):
    hamming_sum = 0
    for inst in range(Y_true.shape[0]):
        hamming_sum += sklearn.metrics.hamming_loss(Y_true[inst,:], Y_predict[inst, :])

    return hamming_sum/Y_true.shape[0]


def accuracy(Y_true, Y_predict):
    jaccard_sum = 0
    for inst in range(Y_true.shape[0]):
        jaccard_sum += sklearn.metrics.jaccard_similarity_score(Y_true[inst,:], Y_predict[inst, :])

    return jaccard_sum/Y_true.shape[0]


def exact_match(Y_true, Y_predict):
    exact_sum = 0
    for inst in range(Y_true.shape[0]):
        if Y_true[inst,:] == Y_predict[inst, :]:
            exact_sum += 1

    return exact_sum / Y_true.shape[0]


def F1_measure(Y_true, Y_predict):
    f1_sum = 0
    for inst in range(Y_true.shape[0]):
        f1_sum += sklearn.metrics.f1_score(Y_true[inst, :], Y_predict[inst, :])

    return f1_sum / Y_true.shape[0]


def macro_f1(Y_true, Y_predict):
    f1_sum = 0
    for l in range(Y_true.shape[1]):
        f1_sum += sklearn.metrics.f1_score(Y_true[:, l], Y_predict[:, l])

    return f1_sum / Y_true.shape[1]


def micro_f1(Y_true, Y_predict):
    numer = 0
    for l in range(Y_true.shape[1]):
        for inst in range(Y_true.shape[0]):
            numer += (Y_true[inst, l] * Y_predict[inst, l])

    numer *= 2

    denom_1 = 0
    denom_2 = 0
    for l in range(Y_true.shape[1]):
        for inst in range(Y_true.shape[0]):
            denom_1 += Y_true[inst, l]

    for l in range(Y_true.shape[1]):
        for inst in range(Y_true.shape[0]):
            denom_2 += (Y_predict[inst, l])

    denom = denom_1 + denom_2

    return numer/denom

if __name__ == "__main__":
    labels_df = pd.read_csv('../../data/outputs/Labels_All_v4_17.csv')
    labels_df = labels_df[(labels_df['Hypertension'] == 1.) | (labels_df['Diabetes'] == 1) | (labels_df['Obesity'] == 1) ]

    kf = KFold(n_splits=5, shuffle=True, random_state=2)

    fold_id = 1
    for train_ids, test_ids in kf.split(labels_df):
        print("--------------Fold-----------------")
        train = (labels_df.iloc[train_ids])[['id', 'Diabetes', 'Hypertension', 'Obesity']]
        test = (labels_df.iloc[test_ids])[['id', 'Diabetes', 'Hypertension', 'Obesity']]

        print(len(test))
        train.to_csv('../../data/outputs/splits/Train_fold_' + str(fold_id) + '.csv')
        test.to_csv('../../data/outputs/splits/Test_fold_' + str(fold_id) + '.csv')

        fold_id += 1


