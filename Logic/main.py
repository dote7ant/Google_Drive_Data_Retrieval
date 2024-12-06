# entry point
import Read_Files as RF
import pandas as pd
from pprint import pprint

url = "https://drive.google.com/drive/folders/1-xpfvjXucQVVNYm4ahbvRXKyVXakCG9G?usp=drive_link"
url1 = "combined_excel_data.csv"
df = pd.read_csv(url1, low_memory=False)
print("The shape of the data is:", df.shape)
pprint(df.tail(10))

# RF.read_files(url)
