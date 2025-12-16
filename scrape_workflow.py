import tqdm
import pandas as pd
import time
import random

from huggingface_scraper import scrape_huggingface_workflow
from get_genai_summaries import get_genai_analysis_json
from save_to_gbq import save_to_gbq

if __name__ == "__main__":
    papers_metadata_list = scrape_huggingface_workflow()
    if len(papers_metadata_list) > 0:
        all_paper_details = []
        for paper_metadata in tqdm.tqdm(papers_metadata_list, desc = "Extracting info from paper using genai..."):
            full_paper_details = get_genai_analysis_json(paper_metadata) 
            all_paper_details.append(full_paper_details)
            time.sleep(8+ 3 * random.random())

        scraped_df = pd.DataFrame(all_paper_details)
        save_status = save_to_gbq(scraped_df)
        print(f"{save_status}: {len(papers_metadata_list)} saved to GBQ")


    