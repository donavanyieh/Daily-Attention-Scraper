import os
from dotenv import load_dotenv
from retry import retry
import litellm
import pandas as pd
import ast

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

PROMPT = """
<CONTEXT>
You are a data science professor. You have a deep expertise in machine learning and AI research, and excel at breaking down technical papers into digestable texts for beginners to understand
<END OF CONTEXT>

<TASK>
You will be a list of research papers published today. The list contains multiple JSONs of information of research papers published today.
Your job is to synthesize this into a TLDR for beginners to read
- Brief Summary: A summary in a 120 words to 150 words of all papers. Just a simple paragraph, with no markdown formatting, e.g. no * and no #
- Impact: Why this matters for a AI practitioner, in 50 to 60 words, in plain text e.g. no * and no #.
- Exciting Topics: 3 to 5 key points where you think the provided research papers has most impact on data science. Each topic is one to two sentence long, and must reference paper title name of any claims, and must have no markdown formatting, e.g. no * and no #

Be clear and mindful of your audience who are beginners, and make them excited about AI.
It is very important that you reference paper TITLES.
Reason and think to use paper titles (typically string) instead of paper id (typically numbers with '.' in the middle), or other paper metadata like tags
<END OF TASK>

<IMPORTANT>
These 3 golden rules are key to performing your task well:
1. This is STRICTLY a data summarization task. Your analysis and answer should be ONLY from the list of reseach papers information provided within this prompt.
2. When making statements, make sure you reference the paper titles appropriately. It is important you reference the paper titles instead of other paper metadata, so that the end user can search it up themselves. This is so the user knows which paper to explore further. REFERENCE THE PAPER TITLE.
3. Think and reason beyond human capability and make sure your answer stays within the context of the research papers provided in this prompt

These golden rules apply when coming up with the summary, impact, and exciting topics. Adhere to these golden rules at all times.
</IMPORTANT>

HERE IS THE LIST OF RESEARCH PAPERS FOR YOUR ANALYSIS
<research papers>
<research_json>
<end of research papers>

<OUTPUT FORMAT>
Give your answer strictly in JSON format only, in the following format:
{"summary": <summary string>, "impact": <impact string>, "exciting topics":<list of 3 to 5 key points of exciting new things STRICTLY FROM PROVIDED LIST OF RESEARCH PAPERS, referencing PAPER TITLES. Follow instructions in TASK and IMPORTANT>}
<END OF OUTPUT FORMAT>
""".strip()

@retry(tries=3, delay=15)
def get_model_response(df, prompt = PROMPT, api_key = API_KEY):

    response = litellm.completion(
        model='gemini/gemini-2.5-flash-preview-09-2025',
        api_key = api_key,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt.replace("<research_json>", f"{df.to_dict('records')}")},
                ],
            }
        ],
    )
    response_json = ast.literal_eval(response.choices[0].message.content.lstrip("```json").rstrip("```").strip())
    return response_json

def get_daily_summary(df):
    daily_summary_json = get_model_response(df)
    daily_summary_json_values = list(daily_summary_json.values())
    
    output_json = [{
        "Summary": daily_summary_json_values[0],
        "Impact": daily_summary_json_values[1],
        "Exciting Topics": daily_summary_json_values[2]
    }]
    daily_summary_df = pd.DataFrame(output_json)
    return daily_summary_df
