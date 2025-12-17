import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import ast
    import tqdm
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import time
    import random
    return (
        BeautifulSoup,
        ast,
        datetime,
        mo,
        random,
        requests,
        time,
        timedelta,
        tqdm,
    )


@app.cell
def _():
    output_json = [{
    "Summary": "test text",
        "Impact": "Test text",
        "Exciting Topics": ["2","3"]
    }]

    import pandas as pd
    pd.DataFrame(output_json)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Part 1: Scrape Huggingface
    """)
    return


@app.cell
def _(datetime, timedelta):
    def get_yesterday_date():
        """
        Get yesterday's date in YYYY-mm-dd format, for passing into bs4 scraper
        """
        yesterday_date_obj = datetime.now() - timedelta(1)
        yesterday_date_str = datetime.strftime(yesterday_date_obj, "%Y-%m-%d")
        return yesterday_date_str
    return (get_yesterday_date,)


@app.cell
def _(BeautifulSoup, requests):
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
    return (scrape_papers_from_date,)


@app.cell
def _(BeautifulSoup, requests):
    def scrape_paper_details(title, page_link):
        """
        Scrapes relevant fields from papers link
        """
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

        return output_dict
    return (scrape_paper_details,)


@app.cell
def _(
    get_yesterday_date,
    random,
    scrape_paper_details,
    scrape_papers_from_date,
    time,
    tqdm,
):
    def scrape_huggingface_workflow():
        date_to_scrape = get_yesterday_date()
        titles_and_links = scrape_papers_from_date(date_to_scrape)
        time.sleep(5 + 5*random.random())

        # Rmove after testing
        titles_and_links = titles_and_links[:3]

        paper_metadata = []
        for title, link in tqdm.tqdm(titles_and_links, desc = "Scraping paper metadata"):
            paper_metadata.append(scrape_paper_details(title, link))
            time.sleep(3 + 3*random.random())

        return paper_metadata
    return (scrape_huggingface_workflow,)


@app.cell
def _(scrape_huggingface_workflow):
    output = scrape_huggingface_workflow()
    output
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Part 2: Gen AI outputs
    """)
    return


@app.cell
def _():
    import os
    return (os,)


@app.cell
def _():

    import shutil
    return (shutil,)


@app.cell
def _():
    import base64
    return (base64,)


@app.cell
def _():
    from dotenv import load_dotenv
    return (load_dotenv,)


@app.cell
def _():
    from retry import retry
    return (retry,)


@app.cell
def _(load_dotenv):
    load_dotenv('../.env')
    return


@app.cell
def _():
    import litellm
    return (litellm,)


@app.cell
def _(os):
    API_KEY = os.environ.get("GEMINI_API_KEY")
    return (API_KEY,)


@app.cell
def _():
    PROMPT = """
    <CONTEXT>
    You are a data science professor. You have a deep expertise in machine learning and AI research, and excel at breaking down technical papers into digestable texts for your AI students and beginner AI practitioners to understand
    <END OF CONTEXT>

    <TASK>
    You will be given a research paper. You are to analyze the research paper, and provide the following 4 fields:
    - Summary: A summary in a 100 words to 120 words
    - Key Points: Key points of this paper that are notable, including data sources, methodology, and results. 5 to 7 key points. 
    - Impact: Why this matters for a AI practitioner, in 50 to 60 words
    - Tags: 1-3 relevant tags from the following available tags: LLMs, Multimodal, Fine Tuning, Code Generation, Multi-Agent Systems, RAG

    The tags must be from the tags provided above. Remember, your audience are technical but beginners.
    <END OF TASK>

    <OUTPUT FORMAT>
    Give your answer strictly in JSON format only, in the following format:
    {"Summary": <summary string>, "Key Points":<list of 6 to 8 key points>, "Impact": <impact string>, "Tags": <List of 1-3 relevant tags from provided tags>}
    <END OF OUTPUT FORMAT>
    """.strip()
    return (PROMPT,)


@app.cell
def _(os, requests, shutil):
    def download_pdf_simple(arxiv_url, filename="temp.pdf"):
        """
        Downloads an arXiv PDF using a direct link.
        """
        # Convert 'abs' URL to 'pdf' URL if necessary
        pdf_url = arxiv_url.replace("/abs/", "/pdf/")
        if not pdf_url.endswith(".pdf"):
            pdf_url += ".pdf"

        try:
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes

            with open(filename, 'wb') as file:
                shutil.copyfileobj(response.raw, file)

            print(f"Successfully downloaded PDF to {os.path.abspath(filename)}")
            return True, os.path.abspath(filename)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during download: {e}")
            return False, ""
    return (download_pdf_simple,)


@app.cell
def _(base64):
    def pdf_to_base64(file_path):
        """
        Converts a PDF file to a base64 encoded string.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The base64 encoded string, decoded to ASCII for display/storage.
        """
        try:
            with open(file_path, "rb") as pdf_file:
                # Read the file in binary mode and encode to base64 bytes
                encoded_bytes = base64.b64encode(pdf_file.read())
                # Decode the bytes to a string (usually 'ascii' or 'utf-8')
                encoded_string = encoded_bytes.decode('ascii')
                return encoded_string
        except IOError as e:
            print(f"Error opening or reading file: {e}")
            return None
    return (pdf_to_base64,)


@app.cell
def _(API_KEY, PROMPT, litellm, retry):
    @retry(tries=3, delay=5)
    def get_model_response(pdf_base64, prompt = PROMPT, api_key = API_KEY):

        response = litellm.completion(
            model='gemini/gemini-2.5-flash-preview-09-2025',
            api_key = api_key,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "file",
                            "file": {
                                "file_data": f"data:application/pdf;base64,{pdf_base64}",
                            }
                        },
                    ],
                }
            ],
        )
        return response
    return (get_model_response,)


@app.cell
def _(ast, download_pdf_simple, get_model_response, pdf_to_base64):
    def get_genai_analysis_json(input_json):
        if "arXiv Page" not in input_json["links"]:
            return False, {}

        download_status, download_path = download_pdf_simple(input_json['links']['arXiv Page']) # replce with link from inpit json
        if not download_status:
            return False, {}

        try:
            pdf_base64 = pdf_to_base64(download_path)
            response = get_model_response(pdf_base64)
            response_json = ast.literal_eval(response.choices[0].message.content.lstrip("```json").rstrip("```").strip())
        except Exception as e:
            print(e)
            return False, {}

        output_json = input_json
        response_values = list(response_json.values())
        output_json['summary'] = response_values[0]
        output_json['keyPoints'] = response_values[1]
        output_json['impact'] = response_values[2]
        output_json['tags'] = response_values[3]

        try:
            desired_order_list = ['id', 'title', 'authors', 'abstract', 'summary', 'keyPoints', 'impact', 'links', 'date', 'upvotes', 'tags']
            reordered_output_json = {k: output_json[k] for k in desired_order_list}
        except:
            return False, {}

        return reordered_output_json
    return (get_genai_analysis_json,)


@app.cell
def _(get_genai_analysis_json, test_output):
    response = get_genai_analysis_json(test_output)
    return (response,)


@app.cell
def _(response):
    response
    return


@app.cell
def _():
    return


app._unparsable_cell(
    r"""
      {
        \"id\": \"2312.24119\",
        \"title\": \"Benchmarking Hallucination Detection Methods\",
        \"authors\": [\"Kevin Zhou\", \"Fatima Noor\"],
        \"abstract\": \"We benchmark hallucination detection methods across QA, summarization, and RAG settings.\",
        \"summary\": \"The study shows that no single method generalizes well, motivating ensemble-based hallucination detectors.\",
        \"keyPoints\": [
          \"Comprehensive hallucination benchmark.\",
          \"Evaluation across tasks.\",
          \"Shows limits of current detectors.\",
          \"Proposes ensemble approaches.\"
        ],
        \"impact\": \"Provides clarity in a noisy space of hallucination mitigation techniques.\",
        \"links\": {
          \"github\": \"https://github.com/hallucination-bench\"
        },
        \"date\": \"2025-12-12\",
        \"upvotes\": 2760,
        \"tags\": [\"Hallucinations\", \"Evaluation\", \"LLMs\"]
      }
    ]
    """,
    name="_"
)


if __name__ == "__main__":
    app.run()
