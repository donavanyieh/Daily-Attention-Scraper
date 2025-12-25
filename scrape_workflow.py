import tqdm
import pandas as pd
import time
import random
import tracemalloc
import os

from huggingface_scraper import scrape_huggingface_workflow, get_yesterday_date
from get_genai_analysis import get_genai_analysis_json
from get_genai_summary import get_daily_summary
from save_to_gbq import save_to_gbq_papers, save_to_gbq_summaries
from generate_podcast import podcast_generation_workflow

if __name__ == "__main__":
    tracemalloc.start()
    print(f"Traced memory on start: {tracemalloc.get_traced_memory()}")
    papers_metadata_list = scrape_huggingface_workflow()
    
    print(f"Traced memory after scraping huggingface: {tracemalloc.get_traced_memory()}")

    if len(papers_metadata_list) > 0:
        all_paper_details = []
        for paper_metadata in tqdm.tqdm(papers_metadata_list, desc = "Extracting info from paper using genai..."):
            genai_analysis_status, full_paper_details = get_genai_analysis_json(paper_metadata) 
            if genai_analysis_status:
                all_paper_details.append(full_paper_details)
                time.sleep(8 + 3*random.random())
            else:
                time.sleep(10 + 5*random.random())
            print(f"Traced memory per iteration of genai: {tracemalloc.get_traced_memory()}")

        scraped_df = pd.DataFrame(all_paper_details)
        save_status = save_to_gbq_papers(scraped_df, os.environ.get('GBQ_PAPERS_TABLE'))
        print(f"{save_status}: {len(papers_metadata_list)} papers saved to GBQ Papers table")

        daily_summary_df = get_daily_summary(scraped_df)
        daily_summary_df['date'] = get_yesterday_date()
        save_status = save_to_gbq_summaries(daily_summary_df, os.environ.get('GBQ_DAILY_SUMMARY_TABLE'))
        print(f"{save_status}: Saved to GBQ daily summary table")
        print("Generating podcast...")
        summary_json = daily_summary_df.to_dict("records")[0]
        podcast_save_status = podcast_generation_workflow(summary_json)
        print(f"Podcast save status: {podcast_save_status}")


        


    