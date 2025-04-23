import os
import datetime
import requests
from fastapi import FastAPI
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv


dotenv_path = Path('.env/.venv')
load_dotenv(dotenv_path=dotenv_path)


file_url = os.getenv('FILE_URL')
bucket_name = os.getenv('BUCKET_NAME')
topic = os.getenv('TOPIC')
template = os.getenv('DESTINATION_BLOB_NAME')
google_project = os.getenv('GOOGLE_PROJECT')

now = datetime.datetime.now()

day_name = now.strftime("%A")

destination_blob_name = template.format(day_name=day_name)


app = FastAPI()


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
                if chunk:
                    blob_file.write(chunk)
        # f"Large file {url} downloaded and uploaded to gs://{bucket_name}/{destination_blob_name}."
        status = "Backup successful 😀"

        notification(status)
        return status

    except requests.exceptions.RequestException as e:
        # f"Error downloading file: {e}"
        status = "Backup failed 😨"
        notification(status)
        return status
    except Exception as e:
        # f"Error uploading to GCS: {e}"
        status = "Backup faliure 💀"
        notification(status)
        return status



def notification(message):
    requests.post(url  = "https://ntfy.sh/" + topic, 
                  data = message.encode(encoding='utf-8')
                 )

    
@app.get("/")   
async def root():
    status = download_and_upload_large_file_to_gcs(file_url, bucket_name, destination_blob_name)
    return {"message" : status}