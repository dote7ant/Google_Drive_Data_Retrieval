# Google Drive Data Retrieval

This project provides a Python script for retrieving and processing Excel files from a specified Google Drive folder. It authenticates with the Google Drive API, lists files in the folder, downloads Excel files, processes them, and optionally combines the data into a single CSV file.

## Features

- Authenticate with Google Drive API using service account credentials
- List all files in a specified Google Drive folder
- Download Excel files (.xls and .xlsx)
- Process and combine data from multiple Excel files
- Save combined data to a CSV file (optional)

## Requirements

- Python 3.6+
- pandas
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

## Setup

1. Clone this repository or download the script.

2. Install the required Python packages:

   ```
   pip install pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. Set up Google Drive API credentials:
   - Go to the Google Cloud Console
   - Create a new project (or select an existing one)
   - Enable the Google Drive API
   - Create a service account and download the JSON key file
   - Rename the key file to `credentials.json` and place it in the same directory as the script

## Usage

1. Run the script:

   ```
   python google_drive_data_retrieval.py
   ```

2. When prompted, enter the Google Drive folder ID or the full folder URL containing the Excel files you want to process.

3. The script will list all files in the folder, download and process Excel files, and display the combined data.

4. You will be asked if you want to save the combined data to a CSV file. Enter 'yes' or 'no' as appropriate.

## Notes

- The script only processes files with Excel MIME types:
  - `application/vnd.ms-excel`
  - `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Files with "EVENT" or "SOLAR" in their names (case-insensitive) are skipped.
- Downloaded files are deleted after processing to save space.

## Troubleshooting

- If you encounter permission errors, ensure that the service account has the necessary permissions to access the Google Drive folder.
- Make sure the `credentials.json` file is in the same directory as the script.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](link-to-your-issues-page) if you want to contribute.

## License

[Specify your license here, e.g., MIT, GPL, etc.]