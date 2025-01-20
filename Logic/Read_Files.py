import os
import re
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from multiprocessing import Pool, cpu_count
import io
import datetime
from tqdm import tqdm
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Google Drive API setup
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
credentials = service_account.Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)


def extract_folder_id(input_string):
    folder_id_pattern = r"([-\w]{25,})"
    match = re.search(folder_id_pattern, input_string)
    return match.group(1) if match else None


def list_files(folder_id):
    files = []
    page_token = None

    try:
        while True:
            query = f"'{folder_id}' in parents"
            response = (
                service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageToken=page_token,
                    pageSize=100,
                )
                .execute()
            )
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
    except HttpError as error:
        logging.error(f"Error fetching file list: {error}")
    return files


def download_file(file):
    try:
        file_id, file_name = file["id"], file["name"]
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        with open(file_name, "wb") as f:
            f.write(fh.read())
        logging.info(f"Downloaded file: {file_name}")
        return file_name
    except HttpError as error:
        logging.error(f"Error downloading {file['name']}: {error}")
        return None


def process_file(file_name):
    try:
        sheets_dict = pd.read_excel(file_name, sheet_name=None)
        os.remove(file_name)  # Clean up after processing
        return (
            pd.concat(sheets_dict.values(), ignore_index=True) if sheets_dict else None
        )
    except Exception as e:
        logging.error(f"Error processing {file_name}: {e}")
        return None


def process_files(folder_id):
    files = list_files(folder_id)
    if not files:
        logging.info("No files found in the specified folder.")
        return

    excel_files = [
        file
        for file in files
        if file["mimeType"]
        in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        and "EVENT" not in file["name"].upper()
        and "SOLAR" not in file["name"].upper()
    ]

    # Calculate optimal number of processes
    num_processes = min(cpu_count(), len(excel_files))

    # Download files first using multiprocessing
    with Pool(processes=num_processes) as pool:
        downloaded_files = list(
            tqdm(
                pool.imap(download_file, excel_files),
                total=len(excel_files),
                desc="Downloading files",
            )
        )

    # Remove None values from failed downloads
    downloaded_files = [f for f in downloaded_files if f is not None]
    t1 = time.perf_counter()
    # Process files using multiprocessing
    with Pool(processes=num_processes) as pool:
        dataframes = list(
            tqdm(
                pool.imap(process_file, downloaded_files),
                total=len(downloaded_files),
                desc="Processing files",
            )
        )
    t2 = time.perf_counter()
    # Combine dataframes
    dataframes = [df for df in dataframes if df is not None]
    if dataframes:
        final_df = pd.concat(dataframes, ignore_index=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Parallel Code Took:{t2 - t1} seconds to execute!")
        print(f"Final DataFrame shape: {final_df.shape}")

        save_option = input("Do you want to save the combined data? (y/n): ").lower()
        if save_option == "y":
            output_file = f"combined_excel_data_{timestamp}.csv"
            final_df.to_csv(output_file, index=False)
            logging.info(f"Combined data saved to {output_file}")
        else:
            print("No data to be processed!!!")


if __name__ == "__main__":
    # Required for Windows systems
    if __name__ == "__main__":
        folder_input = input("Enter the Google Drive folder ID or URL: ")
        folder_id = extract_folder_id(folder_input)
        if folder_id:
            process_files(folder_id)
        else:
            logging.error("Invalid folder ID or URL.")
