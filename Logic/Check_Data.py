import pandas as pd
import handle as h
from pprint import pprint

import warnings

warnings.filterwarnings("ignore")


class DataChecking:
    def __init__(self, df):
        self.df = df

    def check_duplicates(self):
        duplicates = self.df[self.df.duplicated()]
        value = self.df.duplicated().value_counts()
        if duplicates.empty:
            return "No duplicates found."
        else:
            return value

    def check_null_values(self):
        null_values = self.df.columns[self.df.isnull().any()].tolist()
        if not null_values:
            return "No null values found."
        else:
            missing_values = self.df[null_values].isnull().sum()
            result = []
            for column in null_values:
                result.append(f"{column}: {missing_values[column]} missing value(s)")
            return "\n".join(result)

    def check_shape(self):
        rows, cols = self.df.shape
        return f"There are {rows} rows and {cols} columns"

    def check_data_types(self):
        return self.df.dtypes.to_dict()

    def cleaning(self):
        save_option = input("Do you want to clean the data? (y/n): ").lower()
        if save_option == "y":
            cleaner = h.DataPreprocessing(self.df)
            cleaned_df = cleaner.preprocess_data()
            return cleaned_df
        else:
            return self.df

    def checking_data(self):
        results = {
            "shape": self.check_shape(),
            "dtypes": self.check_data_types(),
            "duplicates": self.check_duplicates(),
            "null_values": self.check_null_values(),
        }

        pprint("\n=== Data Quality Report ===")
        pprint("\n1. Data Shape:")
        pprint(results["shape"])

        pprint("\n2. Data Types:")
        pprint(results["dtypes"])

        pprint("\n3. Duplicate Check:")
        pprint(results["duplicates"])

        pprint("\n4. Null Values Check:")
        pprint(results["null_values"])

        pprint("\n=== End of Report ===")
        self.cleaning()
        return self.df, results
