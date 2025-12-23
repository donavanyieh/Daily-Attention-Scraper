import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import json
    import numpy as np
    import ast
    import requests
    import os
    import shutil
    from pathlib import Path
    import pymupdf.layout
    import pymupdf4llm
    import time
    import random
    import tqdm
    return (
        Path,
        ast,
        json,
        os,
        pd,
        pymupdf,
        pymupdf4llm,
        random,
        requests,
        shutil,
        time,
        tqdm,
    )


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


@app.function
def fix_id(df):
    df['id'] = df['id'].astype(str)
    df['id'] = df['id'].apply(lambda x: x.replace(",",""))
    return df


@app.cell
def _(pd):
    all_papers_df = pd.read_csv("all_papers.csv")
    return (all_papers_df,)


@app.cell
def _(all_papers_df):
    all_papers_df_fixed = fix_id(all_papers_df)
    return (all_papers_df_fixed,)


@app.cell
def _(all_papers_df_fixed):
    all_papers_df_fixed
    return


@app.cell
def _(all_papers_df_fixed):
    all_papers_df_fixed_dedup = all_papers_df_fixed.drop_duplicates(subset=['id'],keep='first')[['id','title','links']]
    return (all_papers_df_fixed_dedup,)


@app.cell
def _(all_papers_df_fixed_dedup, ast):
    all_papers_df_fixed_dedup['links'] = all_papers_df_fixed_dedup['links'].apply(lambda x: ast.literal_eval(x)['Paper'])
    return


@app.cell
def _(all_papers_df_fixed_dedup):
    all_papers_df_fixed_dedup2 = all_papers_df_fixed_dedup.reset_index(drop = True)
    return (all_papers_df_fixed_dedup2,)


@app.cell
def _(all_papers_df_fixed_dedup2):
    all_papers_df_fixed_dedup2
    return


@app.cell
def _(pd):
    md_df = pd.read_csv("generated_markdowns.csv")
    md_df_fix_id = fix_id(md_df)
    return (md_df,)


@app.cell
def _(md_df):
    done_md_df1 = md_df[(md_df['markdown_text'].notna()) & (md_df["markdown_text"]!="")]
    return (done_md_df1,)


@app.cell
def _(done_md_df1):
    done_md_df1
    return


@app.cell
def _(done_md_df1):
    md_existing = done_md_df1['id'].to_list()
    return (md_existing,)


@app.cell
def _(all_papers_df_fixed_dedup2, md_existing):
    not_done_df = all_papers_df_fixed_dedup2[~all_papers_df_fixed_dedup2['id'].isin(md_existing)]
    return (not_done_df,)


@app.cell
def _(not_done_df):
    not_done_df_left = not_done_df.reset_index(drop = True)
    not_done_df_left
    return (not_done_df_left,)


@app.cell
def _():
    # not_done_df_left['links'] = not_done_df_left['links'].apply(lambda x: ast.literal_eval(x)["Paper"])
    # not_done_df_left
    return


@app.cell
def _(
    Path,
    download_pdf_simple,
    not_done_df_left,
    pymupdf,
    pymupdf4llm,
    random,
    time,
    tqdm,
):
    all_texts = []

    for row in tqdm.tqdm(not_done_df_left.to_dict("records")):
        link = row['links']
        try:
            save_status, res_text = download_pdf_simple(link)
            with pymupdf.open(res_text) as doc:
                all_texts.append(pymupdf4llm.to_markdown(doc, use_ocr = False))
        except Exception as e:
            print(f"{row['id']} failed: {e}")
            all_texts.append("")

        finally:  
            file_path = Path(res_text)
            file_path.unlink(missing_ok=True)
            time.sleep(3*random.random())
    return (all_texts,)


@app.cell
def _(all_texts):
    len(all_texts)
    return


@app.cell
def _(all_texts, not_done_df_left):
    not_done_df_left['markdown_text'] = all_texts
    not_done_df_left
    return


@app.cell
def _(not_done_df_left):
    not_done_df_left_now = not_done_df_left[['id','title','markdown_text']]
    not_done_df_left_now
    return (not_done_df_left_now,)


@app.cell
def _(not_done_df_left_now):
    not_done_df_left_now_toput = not_done_df_left_now[not_done_df_left_now['markdown_text']!=""]
    not_done_df_left_now_toput
    return (not_done_df_left_now_toput,)


@app.cell
def _():
    from google.oauth2 import service_account
    return (service_account,)


@app.cell
def _(json, os, service_account):
    from dotenv import load_dotenv
    import pandas_gbq

    load_dotenv("../.env")
    SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)
    GBQ_DATASET = os.environ.get('GBQ_DATASET')
    return GBQ_DATASET, SERVICE_ACCOUNT, credentials, pandas_gbq


@app.cell
def _(GBQ_DATASET):
    GBQ_DATASET
    return


@app.cell
def _(GBQ_DATASET, SERVICE_ACCOUNT, credentials, pandas_gbq):
    def save_to_gbq_papers(df, gbq_table, gbq_dataset = GBQ_DATASET):
        try:
            pandas_gbq.to_gbq(
                df,
                destination_table=f"{gbq_dataset}.{gbq_table}",
                project_id=SERVICE_ACCOUNT['project_id'],
                if_exists='append', # Use 'append' to add data without overwriting the table
                credentials = credentials
            )
            return True
        except Exception as e:
            print(f"Failed to write to GBQ papers: {e}")
            return False
    return (save_to_gbq_papers,)


@app.cell
def _(not_done_df_left_now_toput, save_to_gbq_papers):
    save_to_gbq_papers(not_done_df_left_now_toput, "paper_markdowns")
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
