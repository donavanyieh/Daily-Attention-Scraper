import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import json
    import ast
    import litellm
    import os
    import tqdm

    from google import genai
    from google.genai import types
    from PIL import Image
    from google.oauth2 import service_account
    from google.cloud import storage

    from dotenv import load_dotenv
    load_dotenv('../.env')
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    GCS_INFOGRAPHIC_BUCKET_NAME = os.environ.get("GCS_INFOGRAPHIC_BUCKET_NAME")
    GCS_INFOGRAPHIC_SUBDIRECTORY = os.environ.get("GCS_INFOGRAPHIC_SUBDIRECTORY")
    SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)

    INFOGRAPHIC_MASTER_PROMPT = f"""You are a data science expert with a specialty in creating infographics to present technical concepts easily. You will be given a JSON, which contains a summary of AI papers published that day. Your job is to create an infographic that will allow people to understand the day's advancements at a glance.

    Keep the infographic simple, and visually easy to digest. Show a header with a title and a date, and represent the rest of the information in a meaningful and exciting way. Use imagery to represent information where applicable, and let the imagery tell the story. Simplicity is key, follow best UIUX practices, consistant color and make sure it is easy to read (e.g. no color blends or transparent wordings). Use less than 200 words in the infographic. KEEP THINGS SIMPLE AND VISUALLY EASY TO UNDERSTAND.

    Here is the information: <daily_json>"""
    return (
        GCS_INFOGRAPHIC_BUCKET_NAME,
        GCS_INFOGRAPHIC_SUBDIRECTORY,
        INFOGRAPHIC_MASTER_PROMPT,
        credentials,
        genai,
        os,
        pd,
        storage,
        tqdm,
        types,
    )


@app.cell
def _(pd):
    daily_summary_df = pd.read_csv("daily_summaries.csv")
    return (daily_summary_df,)


@app.cell
def _(daily_summary_df):
    daily_summary_df
    return


@app.cell
def _(os, storage):
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
    return (upload_jpg_to_gcs,)


@app.cell
def _(GCS_INFOGRAPHIC_SUBDIRECTORY):
    GCS_INFOGRAPHIC_SUBDIRECTORY
    return


@app.cell
def _(
    GCS_INFOGRAPHIC_BUCKET_NAME,
    GCS_INFOGRAPHIC_SUBDIRECTORY,
    INFOGRAPHIC_MASTER_PROMPT,
    credentials,
    daily_summary_df,
    genai,
    tqdm,
    types,
    upload_jpg_to_gcs,
):
    for daily_json in tqdm.tqdm(daily_summary_df.to_dict("records")):
        client = genai.Client()

        INFOGRAPHIC_PROMPT = INFOGRAPHIC_MASTER_PROMPT.replace("<daily_json>",f"{daily_json}")

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[INFOGRAPHIC_PROMPT],
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
                image_size="2K"
            ),
        )
        )
        output_filename = f"{daily_json['date']}.png"
        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = part.as_image()
                image.save(output_filename)

        upload_jpg_to_gcs(output_filename, GCS_INFOGRAPHIC_BUCKET_NAME, GCS_INFOGRAPHIC_SUBDIRECTORY, credentials)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
