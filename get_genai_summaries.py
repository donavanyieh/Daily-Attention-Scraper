import os
import shutil
import base64
from dotenv import load_dotenv
from retry import retry
import litellm
import requests
import ast
from pathlib import Path

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

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
    response_json = ast.literal_eval(response.choices[0].message.content.lstrip("```json").rstrip("```").strip())
    return response_json

def get_genai_analysis_json(input_json):
    if "arXiv Page" not in input_json["links"]:
        return False, {}

    download_status, download_path = download_pdf_simple(input_json['links']['arXiv Page'])
    if not download_status:
        return False, {}

    try:
        pdf_base64 = pdf_to_base64(download_path)
        response_json = get_model_response(pdf_base64)
    except Exception as e:
        print(f"Failed to get model response: {e}")
        return False, {}
    try:
        file_path = Path(download_path)
        file_path.unlink(missing_ok=True)
    except:
        print("Failed to delete temp file")
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
        not_present_cols = [col for col in desired_order_list if col not in list(output_json.keys())]
        print(f"Reordering failed. Columns missing: {not_present_cols}")
        return False, {}
    
    return reordered_output_json

