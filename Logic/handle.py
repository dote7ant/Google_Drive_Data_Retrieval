import pandas as pd
import month as m
import Check_Data as cd
import warnings
import datetime

warnings.filterwarnings("ignore")


class DataPreprocessing:
    def __init__(self, df):
        self.df = df

    def remove_duplicates(self):
        self.df.drop_duplicates(keep=False, inplace=True)

    def remove_cols(self):
        self.df.drop(
            [
                "Debug140",
                "Debug141",
                "Debug142",
                "Debug143",
                "Debug144",
                "Debug145",
                "Debug146",
                "Debug147",
                "Debug148",
                "Debug149",
                "Debug150",
                "Debug151",
                "Debug152",
                "SOC",
                "SOH",
                "soc",
                "BMSFWUpdateState",
            ],
            axis=1,
            inplace=True,
        )

    def Serial_fill_na(self):
        values = self.df["Serial number"].iloc[0]
        self.df["Serial number"].fillna(value=values, inplace=True)

    def remove_null_values(self):
        self.df.dropna(thresh=50, inplace=True)

    def remove_outliers(self):
        # remove outliers using IQR method
        Q1 = self.df.quantile(0.25)
        Q3 = self.df.quantile(0.75)
        IQR = Q3 - Q1
        self.df = self.df[
            ~((self.df < (Q1 - 1.5 * IQR)) | (self.df > (Q3 + 1.5 * IQR))).any(axis=1)
        ]

    def convert_to_numeric(self):
        # convert columns to numeric
        numeric_columns = [
            "Serial number",
        ]
        self.df[numeric_columns] = self.df[numeric_columns].apply(
            pd.to_numeric, errors="coerce"
        )

    def convert_to_datetime(self):
        # convert 'Date' and 'Time' columns to datetime
        self.df["Time"] = pd.to_datetime(self.df["Time"])
        self.df["Date"] = self.df["Time"].dt.date

        # create month column
        self.df["Month"] = pd.to_datetime(self.df["Time"]).dt.month
        # applying the result function to the dataframe
        self.df["Months"] = self.df.Month.apply(lambda x: m.result(x))

    def handle_missing_values(self):
        # handle missing values
        self.df.fillna(self.df.mean(), inplace=True)

    def create_csv(self):
        checker = cd.DataChecking(self.df)
        print(checker.check_shape())
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.df.to_csv(f"cleaned_data_{timestamp}.csv", index=False)
        print("CSV file created successfully.")

    def preprocess_data(self):
        self.remove_duplicates()
        self.remove_cols()
        self.remove_null_values()
        self.Serial_fill_na()
        # self.remove_outliers()
        # self.convert_to_numeric()
        self.convert_to_datetime()
        self.create_csv()
        # self.handle_missing_values()
        return self.df
