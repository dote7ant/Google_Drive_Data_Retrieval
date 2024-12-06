import os
import re
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

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
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.seek(0)
        with open(file_name, "wb") as f:
            f.write(fh.read())
        print(f"Downloaded {file_name}")
        return True
    except HttpError as error:
        print(f"An error occurred while downloading {file_name}: {error}")
        return False


def process_files(folder_id):
    """Retrieve and process all Excel files from the specified Google Drive folder."""
    files = list_files(folder_id)
    if not files:
        print("No files to process.")
        return

    dfs = []
    total_rows = 0

    for file in files:
        file_name = file["name"]
        file_id = file["id"]
        mime_type = file["mimeType"]

        # Skip non-Excel files
        if mime_type not in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/msword",  # Consider removing this if not needed
        ]:
            print(f"Skipping non-Excel file: {file_name}")
            continue

        # Skip specific files based on naming
        if "EVENT" in file_name.upper() or "SOLAR" in file_name.upper():
            print(f"Skipping excluded file: {file_name}")
            continue

        print(f"\nProcessing file: {file_name}")

        try:
            if download_file(file_id, file_name):
                try:
                    # Read all sheets from the Excel file
                    sheets_dict = pd.read_excel(file_name, sheet_name=None)

                    # Combine all sheets from this file
                    if sheets_dict:
                        file_df = pd.concat(sheets_dict.values(), ignore_index=True)
                        print(f"File {file_name} shape: {file_df.shape}")
                        total_rows += file_df.shape[0]
                        dfs.append(file_df)

                except Exception as e:
                    print(f"Error processing file {file_name}: {str(e)}")
                finally:
                    # Clean up downloaded file
                    if os.path.exists(file_name):
                        os.remove(file_name)
        except Exception as e:
            print(f"Error downloading file {file_name}: {str(e)}")

    # Combine all dataframes at the end
    if dfs:
        final_df = pd.concat(dfs, axis=0, ignore_index=True)
        print("\nCombined DataFrame Summary:")
        print(f"Number of files processed: {len(dfs)}")
        print(f"Total rows from individual files: {total_rows}")
        print(f"Final DataFrame shape: {final_df.shape}")

        # Verify row counts match
        if total_rows != final_df.shape[0]:
            print("WARNING: Row count mismatch detected!")
            print(f"Expected rows: {total_rows}")
            print(f"Actual rows: {final_df.shape[0]}")

        # Display column information
        print("\nColumns in final DataFrame:")
        for col in final_df.columns:
            print(f"- {col}: {final_df[col].dtype}")

        # Ask user if they want to save
        save_option = input(
            "Do you want to save the combined data to a CSV file? (yes/no): "
        ).lower()
        if save_option == "yes":
            output_file = "combined_excel_data.csv"
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
