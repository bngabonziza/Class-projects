import pandas as pd

labels = pd.read_csv('../../data/outputs/Labels_All.csv')
ehr = pd.read_csv('../../data/outputs/EHR_records_All_v4_17.csv')

ehr_id_map = {}
for idx, row in ehr.iterrows():
    ehr_id_map[row.ix[1]] = row.ix[0]  # ehr id -> pandas id (EHR file)

df_labels_new = pd.DataFrame(columns=labels.columns)
for idx, row in labels.iterrows():
    row['id'] = ehr_id_map[row['id']]  # replace ehr id BY corresponding pandas id
    df_labels_new = df_labels_new.append(row)

df_labels_new.to_csv('../../data/outputs/Labels_All_v4_17.csv')

