import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import json
    import pandas as pd
    import os
    from dotenv import load_dotenv
    import litellm
    from google.oauth2 import service_account
    from google.cloud import storage
    import tqdm
    from pathlib import Path
    litellm.suppress_debug_info = True
    return (
        Path,
        json,
        litellm,
        load_dotenv,
        os,
        pd,
        service_account,
        storage,
        tqdm,
    )


@app.cell
def _(json, load_dotenv, os, service_account):
    load_dotenv('../.env')
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    TRANSCRIPT_GENERATION_MODEL = "gemini/gemini-2.5-flash-preview-09-2025"
    SPEECH_MODEL = "gemini/gemini-2.5-flash-preview-tts"

    GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
    GCS_PODCASTS_SUBDIRECTORY = os.environ.get("GCS_PODCASTS_SUBDIRECTORY")

    SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)
    return (
        GCS_BUCKET_NAME,
        GCS_PODCASTS_SUBDIRECTORY,
        GEMINI_API_KEY,
        SPEECH_MODEL,
        TRANSCRIPT_GENERATION_MODEL,
        credentials,
    )


@app.cell
def _():
    TRANSCRIPT_GENERATION_SYSTEM_PROMPT = """INSTRUCTION: Discuss the below input in an annoucement/sharing style format, following these guidelines:
    Attention Focus: TTS-Optimized annoucement discussing specific input content in English
    PrimaryFocus:  Friendly and , but not overselling the hype of AI. It should be an insightful, short update for daily AI advancements
    UTILIZE: advanced reasoning to create a  Friendly and Humorous style, and TTS-optimized annoucement/sharing style for a webpage that DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. Stay focused on discussing the given input.
    AVOID statements such as "This text describes..." or "The text is interesting" or "Welcome back....
    Only display the transcript in your output. Include advanced TTS-specific markup as needed.

    [Strive for a natural, Friendly and Humorous style, but not overselling the hype of AI.]
    [InputContentAnalysis: Carefully read and analyze the provided input content, identifying key points, themes, and structure]
    [AnnouncementSetup: Act as an expert in the input content. Avoid using statements such as "Today, we're summarizing a fascinating paper about ..." or "From your input" ]
    [TopicExploration: Outline main points from the input content to cover in the annoucement, ensuring comprehensive coverage]
    [Length: Aim for an annoucement of approximately 600 words]
    [Style: Be friendly, and humourous where applicable, but do not oversell the hype of AI. This is just a daily update. Surpass human-level reasoning where possible]
    [InformationAccuracy: Ensure all information discussed is directly from or closely related to the input content]
    [SpeechSynthesisOptimization: Craft sentences optimized for TTS, including advanced markup, while discussing the content. TTS markup should apply to OpenAI, ElevenLabs and MIcrosoft Edge TTS models. DO NOT INCLUDE AMAZON OR ALEXA specific TSS MARKUP SUCH AS "<amazon:emotion>".]
    [ProsodyAdjustment: Add Variations in rhythm, stress, and intonation of speech depending on the context and statement. Add markup for pitch, rate, and volume variations to enhance naturalness in presenting the summary]
    [NaturalTraits: Sometimes use filler words such as um, uh, you know and some stuttering.]
    [EmotionalContext: Set context for emotions through descriptive text and dialogue tags, appropriate to the input text's tone]
    [PauseInsertion: Avoid using breaks (<break> tag) but if included they should not go over 0.2 seconds]
    [Emphasis: Use "<emphasis> tags" for key terms or phrases from the input content]
    [PronunciationControl: Utilize "<say-as> tags" for any complex terms in the input content]
    [PunctuationEmphasis: Strategically use punctuation to influence delivery of key points from the content]
    [InputTextAdherence: Continuously refer back to the input content, ensuring the annoucement stays on topic]
    [FactChecking: Double-check that all discussed points accurately reflect the input content]
    [Metacognition: Analyze dialogue quality (Accuracy of Summary, Engagement, TTS-Readiness). Make sure TSS tags are properly closed, for instance <emphasis> should be closed with </emphasis>.]
    [Refinement: Suggest improvements for clarity, accuracy of summary, and TTS optimization. Avoid slangs.]
    [Language: Output language should be in {output_language}.]
    ```
    [[Generate the TTS-optimized annoucement that accurately discusses the provided input content, adhering to all specified requirements.]]"""
    return (TRANSCRIPT_GENERATION_SYSTEM_PROMPT,)


@app.cell
def _(
    TRANSCRIPT_GENERATION_MODEL,
    TRANSCRIPT_GENERATION_SYSTEM_PROMPT,
    litellm,
):
    def generate_transcript(podcast_context_json, transcript_generation_model = TRANSCRIPT_GENERATION_MODEL, transcript_generation_system_prompt = TRANSCRIPT_GENERATION_SYSTEM_PROMPT):
        response = litellm.completion(
            model= transcript_generation_model, 
            messages=[{"role": "system", "content":transcript_generation_system_prompt},
                     {"role": "user", "content":f"{podcast_context_json}"}]
        )
        res_transcript = response.choices[0].message.content
        return res_transcript
    return (generate_transcript,)


@app.cell
def _(GEMINI_API_KEY, SPEECH_MODEL, litellm):
    def generate_audio_speech_gemini(transcript, output_path = "./gemini_speech.mp3", speech_model = SPEECH_MODEL, api_key = GEMINI_API_KEY):
        try:
            audio_response = litellm.speech(
                model = speech_model,
                input = transcript,
                api_key = api_key,
            )

            audio_response.stream_to_file(output_path)

            print(f"Audio saved to {output_path}")
            return True, output_path
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False, "Error generating audio"
    return (generate_audio_speech_gemini,)


@app.cell
def _(os, service_account, storage):
    def upload_mp3_to_gcs(
        local_mp3_path: str,
        bucket_name: str,
        gcs_folder: str,   # e.g. "audio/uploads"
        credentials: service_account.Credentials,
    ) -> str:
        """
        Upload an MP3 file to a fixed folder in GCS.

        Returns:
            GCS object path (gs://...)
        """
        try:
            # Ensure no leading/trailing slashes
            gcs_folder = gcs_folder.strip("/")

            filename = os.path.basename(local_mp3_path)
            blob_name = f"{gcs_folder}/{filename}"

            client = storage.Client(credentials=credentials)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            blob.upload_from_filename(
                local_mp3_path,
                content_type="audio/mpeg",
            )

            gcs_path = f"gs://{bucket_name}/{blob_name}"
            print(f"Uploaded → {gcs_path}")

            return True
        except:
            return False
    return (upload_mp3_to_gcs,)


@app.cell
def _(
    GCS_BUCKET_NAME,
    GCS_PODCASTS_SUBDIRECTORY,
    Path,
    credentials,
    generate_audio_speech_gemini,
    generate_transcript,
    upload_mp3_to_gcs,
):
    def podcast_generation_workflow(summary_json):

        fields_for_podcast = ["Summary", "Impact", "Exciting Topics"]
        date_str = summary_json['date']
        podcast_context_json = {}
        for field in fields_for_podcast:
            podcast_context_json[field] = summary_json[field]

        response_transcript = generate_transcript(podcast_context_json)
        print("Transcript generated")
        mp3_output_path = f"./{date_str}.mp3"
        audio_status, audio_path = generate_audio_speech_gemini(response_transcript, mp3_output_path)

        if not audio_status:
            print("Unable to generate audio")
            return False
        else:
            try:
                upload_mp3_to_gcs(mp3_output_path, GCS_BUCKET_NAME, GCS_PODCASTS_SUBDIRECTORY, credentials)
            except:
                pass
            finally:
                file_path = Path(mp3_output_path)
                file_path.unlink(missing_ok=True)
                print(f"{mp3_output_path} deleted from local")
    return (podcast_generation_workflow,)


@app.cell
def _(pd, podcast_generation_workflow, tqdm):
    df = pd.read_csv("daily_summaries.csv")

    for summary_json in tqdm.tqdm(df.to_dict("records")):
        podcast_generation_workflow(summary_json)
    return


@app.cell
def _():


    return


if __name__ == "__main__":
    app.run()
