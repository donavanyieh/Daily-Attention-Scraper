import pandas as pd
import os
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image
import json
from save_to_gcs import upload_jpg_to_gcs
from google.oauth2 import service_account

from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GCS_INFOGRAPHIC_BUCKET_NAME = os.environ.get("GCS_INFOGRAPHIC_BUCKET_NAME")
GCS_INFOGRAPHIC_SUBDIRECTORY = os.environ.get("GCS_INFOGRAPHIC_SUBDIRECTORY")
SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)

INFOGRAPHIC_MASTER_PROMPT = f"""You are a data science expert with a specialty in creating infographics to present technical concepts easily. You will be given a JSON, which contains a summary of AI papers published that day. Your job is to create an infographic that will allow people to understand the day's advancements at a glance.
Keep the infographic simple, and visually easy to digest. Show a header with a title and a date, and represent the rest of the information in a meaningful and exciting way. Use imagery to represent information where applicable, and let the imagery tell the story. Simplicity is key, follow best UIUX practices, consistant color and make sure it is easy to read (e.g. no color blends or transparent wordings). Use less than 200 words in the infographic. KEEP THINGS SIMPLE AND VISUALLY EASY TO UNDERSTAND.
Here is the information: <daily_json>"""


def infographic_generation_workflow(daily_json):
    client = genai.Client()

    INFOGRAPHIC_PROMPT = INFOGRAPHIC_MASTER_PROMPT.replace("<daily_json>",f"{daily_json}")
    try:
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

        save_status = upload_jpg_to_gcs(output_filename, GCS_INFOGRAPHIC_BUCKET_NAME, GCS_INFOGRAPHIC_SUBDIRECTORY, credentials)
    except Exception as e:
        save_status = False
        print(f"Error generating image: {e}")
    finally:
        file_path = Path(output_filename)
        file_path.unlink(missing_ok=True)
        print(f"{output_filename} deleted from local instance")

    return save_status