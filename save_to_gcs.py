from google.oauth2 import service_account
from google.cloud import storage
import json
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
GCS_PODCAST_BUCKET_NAME = os.environ.get("GCS_PODCAST_BUCKET_NAME")
GCS_PODCASTS_SUBDIRECTORY = os.environ.get("GCS_PODCASTS_SUBDIRECTORY")
GCS_INFOGRAPHIC_BUCKET_NAME = os.environ.get("GCS_INFOGRAPHIC_BUCKET_NAME")
GCS_INFOGRAPHIC_SUBDIRECTORY = os.environ.get("GCS_INFOGRAPHIC_BUCKET_NAME")


SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)

def upload_mp3_to_gcs(local_mp3_path, bucket_name, gcs_folder, credentials):
    try:
        # Ensure no leading/trailing slashes
        gcs_folder = gcs_folder.strip("/")

        filename = os.path.basename(local_mp3_path)
        blob_name = f"{gcs_folder}/{filename}"

        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(
            local_mp3_path,
            content_type="audio/mpeg",
        )

        gcs_path = f"gs://{bucket_name}/{blob_name}"
        print(f"Uploaded to {gcs_path}")

        return True
    except:
        return False
    
def upload_jpg_to_gcs(local_jpg_path, bucket_name, gcs_folder, credentials):
    try:
        # Normalize folder path
        gcs_folder = gcs_folder.strip("/")

        filename = os.path.basename(local_jpg_path)
        blob_name = f"{gcs_folder}/{filename}"

        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(
            local_jpg_path,
            content_type="image/jpeg",
        )

        gcs_path = f"gs://{bucket_name}/{blob_name}"
        print(f"Uploaded to {gcs_path}")

        return True

    except Exception as e:
        print(f"Upload failed: {e}")
        return False