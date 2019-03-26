import pandas as pd

df = pd.DataFrame(columns=['lib', 'qty1', 'qty2'])
for i in range(5):
    df.loc[i] = [2 for n in range(3)]

print(df)