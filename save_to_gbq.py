from google.oauth2 import service_account
from dotenv import load_dotenv
import os
import json
import pandas_gbq

load_dotenv()
SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)
GBQ_DATASET = os.environ.get('GBQ_DATASET')

def save_to_gbq_papers(scraped_df, gbq_table, gbq_dataset = GBQ_DATASET):
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
            destination_table=f"{gbq_dataset}.{gbq_table}",
            project_id=SERVICE_ACCOUNT['project_id'],
            if_exists='append', # Use 'append' to add data without overwriting the table
            credentials = credentials
        )
        return True
    except Exception as e:
        print(f"Failed to write to GBQ papers: {e}")
        return False
    
def save_to_gbq_summaries(summary_df, gbq_table, gbq_dataset = GBQ_DATASET):
    try:
        columns_to_json = ["Exciting Topics"]
        for col in columns_to_json:
            summary_df[col] = summary_df[col].apply(lambda x: json.dumps(x))
    except:
        print("Failed to process columns")
        return False
    
    try:
        pandas_gbq.to_gbq(
            summary_df,
            destination_table=f"{gbq_dataset}.{gbq_table}",
            project_id=SERVICE_ACCOUNT['project_id'],
            if_exists='append',
            credentials = credentials
        )
        return True
    except Exception as e:
        print(f"Failed to write to GBQ papers: {e}")
        return False
    

def save_full_markdown_to_gbq(markdown_df, gbq_table, gbq_dataset = GBQ_DATASET):    
    try:
        pandas_gbq.to_gbq(
            markdown_df,
            destination_table=f"{gbq_dataset}.{gbq_table}",
            project_id=SERVICE_ACCOUNT['project_id'],
            if_exists='append',
            credentials = credentials
        )
        return True
    except Exception as e:
        print(f"Failed to write to GBQ markdown table: {e}")
        return False