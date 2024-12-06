# checking the data

import pandas as pd
import glob

url = ""

df = pd.read_excel(url)

print("******************Executing**********************")
print("******************Calculating**********************")
print(f"Shape of the dataframe is:", df.shape)
