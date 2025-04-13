import os, sys
import datetime
import requests
from google.cloud import storage
import io

from pathlib import Path
from dotenv import load_dotenv


dotenv_path = Path('.env/.venv')
load_dotenv(dotenv_path=dotenv_path)


# Example usage:
file_url = os.getenv('FILE_URL')
bucket_name = os.getenv('BUCKET_NAME')

now = datetime.datetime.now()
day_name = now.strftime("%A")


# gzip > /home/sergio/backups/database_`date +%a`.sql.gz
destination_blob_name = 'database_' + day_name + '.sql.gz' #os.getenv('DESTINATION_BLOB_NAME')
#destination_blob_name = os.getenv('DESTINATION_BLOB_NAME')

# how will work this shit in gcp
google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
google_project = os.getenv('GOOGLE_PROJECT')


#Example for large files using chunks.
def download_and_upload_large_file_to_gcs(url, bucket_name, destination_blob_name, chunk_size=8192):
    """Downloads a potentially large file from a URL and uploads it to Google Cloud Storage using chunks."""

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        storage_client = storage.Client(project=google_project)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        with blob.open("wb") as blob_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk: # filter out keep-alive new chunks
                    blob_file.write(chunk)

        print(f"Large file {url} downloaded and uploaded to gs://{bucket_name}/{destination_blob_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except Exception as e:
        print(f"Error uploading to GCS: {e}")


def notification(message):
    """Send a notification to a webhook or any other service."""
    # Implement your notification logic here
    # For example, you can use requests.post() to send a message to a webhook
    print("Notification sent.")

if __name__ == '__main__':
    # Example usage for large files:
    print("Starting download and upload process for large files...") # put an hour for debuf propurses
    download_and_upload_large_file_to_gcs(file_url, bucket_name, destination_blob_name)