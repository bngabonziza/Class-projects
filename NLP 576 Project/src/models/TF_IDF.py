import math
from textblob import TextBlob as tb
import psycopg2
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

tokenize = lambda doc: doc.lower().split(" ")


def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


def main():
    ehr_tags = pd.read_csv('../../data/outputs/EHR_tags.csv')
    ehr_tags.diseases.replace(np.NaN, '[]', inplace=True)
    ehr_tags.medications.replace(np.NaN, '[]', inplace=True)
    ehr_tags.symptoms.replace(np.NaN, '[]', inplace=True)

    doc_dis_List = ehr_tags['diseases'].tolist()
    doc_med_List = ehr_tags['medications'].tolist()
    doc_symp_List = ehr_tags['symptoms'].tolist()

    sklearn_tfidf = TfidfVectorizer(norm='l2', min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True,
                                    tokenizer=tokenize)
    ''' Take the top 10 disease/symptoms/medicines by TF-IDF as features '''

    ###################################################################################
    tfidf_dis = (sklearn_tfidf.fit_transform(doc_dis_List)).toarray()
    ehr_tags['disease_tfidf'] = tfidf_dis.tolist()

    print(len(sklearn_tfidf.vocabulary_))

    ###################################################################################
    tfidf_med = (sklearn_tfidf.fit_transform(doc_med_List)).toarray()
    ehr_tags['medications_tfidf'] = tfidf_med.tolist()

    print(len(sklearn_tfidf.vocabulary_))

    ###################################################################################
    tfidf_symp = (sklearn_tfidf.fit_transform(doc_symp_List)).toarray()
    ehr_tags['symptoms_tfidf'] = tfidf_symp.tolist()

    print(len(sklearn_tfidf.vocabulary_))

    # ehr_tags.to_pickle('../../data/outputs/EHR_tags_tfidf.pickle')

if __name__ == "__main__":
    main()