
import tqdm
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random
from retry import retry

def get_yesterday_date():
    """
    Get yesterday's date in YYYY-mm-dd format, for passing into bs4 scraper
    """
    yesterday_date_obj = datetime.now() - timedelta(1)
    yesterday_date_str = datetime.strftime(yesterday_date_obj, "%Y-%m-%d")
    return yesterday_date_str

def scrape_papers_from_date(date_str):
    """
    Scrapes yesterday's huggingface papers, and returns a list of tuples where

    Args:
        date (str): Date in format YYYY-MM-DD

    Returns:
        List[Tuple[str, str]]: List of tuples, where each tuple contains a paper's title and huggingface link
    """
    response = requests.get(f"https://huggingface.co/papers/date/{date_str}")
    soup = BeautifulSoup(response.content, 'html.parser')
    title_cards = soup.find_all("a", {"class": "line-clamp-3 cursor-pointer text-balance"})

    papers_title_link_list = []
    for card in title_cards:
        papers_title_link_list.append((card.text, f"https://huggingface.co{card['href']}"))

    return papers_title_link_list

@retry(tries=3, delay=5)
def scrape_paper_details(title, page_link):
    """
    Scrapes relevant fields from papers link
    """
    try:
        res = requests.get(page_link)
        soup = BeautifulSoup(res.content, "html.parser")
        
        # Parse upvotes
        upvotes = int(soup.find_all("div", {"class": "font-semibold text-orange-500"})[0].text)
        
        # Parse authors
        raw_authors = soup.find_all("button", {"class":"whitespace-nowrap underline decoration-gray-300 decoration-dashed decoration-2 underline-offset-2 hover:decoration-black dark:decoration-gray-500 dark:hover:decoration-white"})
        authors = [author.text.strip() for author in raw_authors]
        
        # Parse abstract
        abstract = soup.find_all("p", {"class": "text-gray-600"})[0].text
        
        # Parse links
        raw_links = soup.find_all("a", {"class": "btn inline-flex h-9 items-center"})
        page_links_dict = {}
        for link in raw_links:
            if "arxiv" in link.text.lower():
                page_links_dict["arXiv Page"] = link["href"]
            elif "view pdf" in link.text.lower():
                page_links_dict["Paper"] = link["href"]
            elif "github" in link.text.lower():
                page_links_dict["GitHub"] = link["href"]
            elif "project" in link.text.lower():
                page_links_dict['Project Page'] = link['href']

        output_dict = {
            "id": page_link.split("/")[-1],
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "links": page_links_dict,
            "upvotes": upvotes
        }
    except Exception as e:
        print(e)
        return {}
    
    return output_dict

def scrape_huggingface_workflow():
    date_to_scrape = get_yesterday_date()
    titles_and_links = scrape_papers_from_date(date_to_scrape)
    time.sleep(5 + 5*random.random())
    all_paper_metadata = []
    for title, link in tqdm.tqdm(titles_and_links, desc = "Scraping paper metadata"):
        paper_metadata = scrape_paper_details(title, link)
        if len(paper_metadata) == 0:
            time.sleep(8 + random.random())
        else:
            paper_metadata['date'] = date_to_scrape
            all_paper_metadata.append(paper_metadata)
            time.sleep(3 + 3*random.random())
        
    return all_paper_metadata