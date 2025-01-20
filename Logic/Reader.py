import os
import re
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
import datetime
from tqdm import tqdm
import time

# set up Google Drive API authentication
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
credentials = service_account.Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)
service = build("drive", "v3", credentials=credentials)


def extract_folder_id(input_string):
    """extract the folder ID from a Google Drive URL or folder ID string."""
    folder_id_pattern = r"([-\w]{25,})"
    match = re.search(folder_id_pattern, input_string)
    return match.group(1) if match else None


def list_files(folder_id):
    """list all files in the specified Google Drive folder."""
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
                    pageSize=1000,
                )
                .execute()
            )

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")

            if not page_token:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

    if not files:
        print("No files found in the specified folder.")
    else:
        print(f"Found {len(files)} file(s) in the drive folder:")
        for file in files:
            print(f"- {file['name']} (Type: {file['mimeType']})")

    return files


def download_file(file_id, file_name):
    """retrieve a file from Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        with tqdm(
            total=100, desc=f"Downloading {file_name}", unit="%", unit_scale=True
        ) as pbar:
            while done is False:
                status, done = downloader.next_chunk()
                progress = int(status.progress() * 100)
                pbar.update(progress - pbar.n)

        fh.seek(0)
        with open(file_name, "wb") as f:
            f.write(fh.read())
        return True

    except HttpError as error:
        print(f"An error occurred while downloading {file_name}: {error}")
        return False


def process_files(folder_id):
    """Retrieve and process all Excel files from the specified Google Drive folder."""
    files = list_files(folder_id)
    if not files:
        print("No files found in the specified folder.")
        return

    # Filter Excel files and exclude specific names
    excel_files = [
        file
        for file in files
        if file["mimeType"]
        in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/msword",
        ]
        and "EVENT" not in file["name"].upper()
        and "SOLAR" not in file["name"].upper()
    ]

    if not excel_files:
        print("No Excel files to process.")
        return

    dfs = []
    total_rows = 0

    t1 = time.perf_counter()

    # Process files sequentially instead of using ThreadPoolExecutor
    for file in tqdm(excel_files, desc="Processing files"):
        try:
            if download_file(file["id"], file["name"]):
                try:
                    sheets_dict = pd.read_excel(file["name"], sheet_name=None)
                    if sheets_dict:
                        file_df = pd.concat(sheets_dict.values(), ignore_index=True)
                        print(f"File {file['name']} shape: {file_df.shape}")
                        dfs.append(file_df)
                        total_rows += file_df.shape[0]
                except Exception as e:
                    print(f"Error processing file {file['name']}: {e}")
                finally:
                    if os.path.exists(file["name"]):
                        os.remove(file["name"])
        except Exception as e:
            print(f"Error downloading file {file['name']}: {e}")

    t2 = time.perf_counter()

    # Combine all dataframes
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        print("\nCombined DataFrame Summary:")
        print(f"Number of files processed: {len(dfs)}")
        print(f"Total rows from individual files: {total_rows}")
        print(f"Final DataFrame shape: {final_df.shape}")

        print(f"Sequential Code Took:{t2 - t1} seconds")
        # Display column information
        print("\nColumns in final DataFrame:")
        for col in final_df.columns:
            print(f"- {col}: {final_df[col].dtype}")

        save_option = input(
            "Do you want to save the combined data to a CSV file? (yes/no): "
        ).lower()
        if save_option == "yes":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"combined_excel_data_{timestamp}.csv"
            final_df.to_csv(output_file, index=False)
            print(f"Combined data saved to {output_file}")
    else:
        print("No data to process.")


# execution
if __name__ == "__main__":
    folder_input = input("Enter the Google Drive folder ID or full folder URL: ")
    folder_id = extract_folder_id(folder_input)

    if folder_id:
        print(f"Using folder ID: {folder_id}")
        process_files(folder_id)
    else:
        print("Invalid folder ID or URL. Please check your input and try again.")
