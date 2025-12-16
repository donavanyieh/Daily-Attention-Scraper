from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import json
import pandas_gbq

load_dotenv()
SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)

def save_to_gbq(scraped_df):
    try:
        columns_to_json = ["authors", "keyPoints", "links", "tags"]
        for col in columns_to_json:
            scraped_df[col] = scraped_df[col].apply(lambda x: json.dumps(x))
    except:
        print("Failed to process columns")
        return False
    
    try:
        pandas_gbq.to_gbq(
            scraped_df,
            destination_table=f"{os.environ.get('GBQ_DATASET')}.{os.environ.get('GBQ_TABLE')}",
            project_id=SERVICE_ACCOUNT['project_id'],
            if_exists='append', # Use 'append' to add data without overwriting the table
            credentials = credentials
        )
        return True
    except Exception as e:
        print(f"Failed to write to GBQ: {e}")
        return False