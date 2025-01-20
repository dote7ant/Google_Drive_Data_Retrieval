import pandas as pd
import Check_Data as cd
import os
import glob
from datetime import datetime
import time


def create_df(url):
    df = pd.read_csv(url)
    checker = cd.DataChecking(df)
    checked_df = checker.checking_data()
    return checked_df


def find_latest_file(directory):
    # look for files matching the pattern
    pattern = "combined_excel_data_*.csv"
    matching_files = glob.glob(os.path.join(directory, pattern))

    if not matching_files:
        return None

    # get the most recent file
    current_time = os.path.getmtime
    latest_file = max(matching_files, key=current_time)
    return latest_file


def confirm_file_processing():
    # get the current directory or specify your directory path
    directory = os.getcwd()  # or your specific path

    latest_file = find_latest_file(directory)

    if latest_file is None:
        print("No matching files found.")
        return None

    # get the file's last modified time
    mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))

    # user confirmation
    print(f"\nFound latest file: {os.path.basename(latest_file)}")
    print(f"Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        response = input("\nWould you like to process this file? (y/n): ").lower()
        if response in ["y", "n"]:
            break
        print("Please enter 'y' for yes or 'n' for no.")

    if response == "y":
        return latest_file
    return None


if __name__ == "__main__":
    file_to_process = confirm_file_processing()
    if file_to_process:
        df = create_df(file_to_process)
        # Continue with your analysis
