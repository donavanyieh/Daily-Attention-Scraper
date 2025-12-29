import json
import os
from dotenv import load_dotenv
import litellm
from google.oauth2 import service_account
from pathlib import Path
from save_to_gcs import upload_mp3_to_gcs
litellm.suppress_debug_info = True

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TRANSCRIPT_GENERATION_MODEL = "gemini/gemini-2.5-flash-preview-09-2025"
SPEECH_MODEL = "gemini/gemini-2.5-flash-preview-tts"

GCS_PODCAST_BUCKET_NAME = os.environ.get("GCS_PODCAST_BUCKET_NAME")
GCS_PODCASTS_SUBDIRECTORY = os.environ.get("GCS_PODCASTS_SUBDIRECTORY")


SERVICE_ACCOUNT = json.loads(os.environ.get("GBQ_SERVICE_ACCOUNT"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT)

TRANSCRIPT_GENERATION_SYSTEM_PROMPT = """INSTRUCTION: Discuss the below input in an annoucement/sharing style format, following these guidelines:
Attention Focus: TTS-Optimized annoucement discussing specific input content in English
PrimaryFocus:  Insightful, short update for daily AI advancements. You are NOT selling anything. Just be straightforward. Be useful to the audience, who are technical users of different backgrounds (software engineers, AI engineers, computer vision experts, LLM evaluation experts etc).
UTILIZE: advanced reasoning to create a transcript that is useful and straightforward, and TTS-optimized annoucement/sharing style for a webpage that DISCUSSES THE PROVIDED INPUT CONTENT. Do not generate content on a random topic. Stay focused on discussing the given input.
AVOID statements such as "This text describes..." or "The text is interesting" or "Welcome back....
Only display the transcript in your output. Include advanced TTS-specific markup as needed.

[Strive for a natural, insightful, straightforward daily update.]
[InputContentAnalysis: Carefully read and analyze the provided input content, identifying key points, themes, and structure]
[AnnouncementSetup: Act as an expert in the input content. Avoid using statements such as "Today, we're summarizing a fascinating paper about ..." or "From your input" ]
[TopicExploration: Outline main points from the input content to cover in the annoucement, ensuring comprehensive coverage]
[Length: Aim for an annoucement of approximately 600 words]
[Style: This is just a daily update for a technical audience. Surpass human-level reasoning where possible]
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
[Language: Output language should be in english.]
```
[[Generate the TTS-optimized annoucement that accurately discusses the provided input content, adhering to all specified requirements.]]"""

def generate_transcript(podcast_context_json, transcript_generation_model = TRANSCRIPT_GENERATION_MODEL, transcript_generation_system_prompt = TRANSCRIPT_GENERATION_SYSTEM_PROMPT):
    response = litellm.completion(
        model= transcript_generation_model, 
        messages=[{"role": "system", "content":transcript_generation_system_prompt},
                 {"role": "user", "content":f"{podcast_context_json}"}]
    )
    res_transcript = response.choices[0].message.content
    return res_transcript

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
            save_status = upload_mp3_to_gcs(audio_path, GCS_PODCAST_BUCKET_NAME, GCS_PODCASTS_SUBDIRECTORY, credentials)
        except:
            pass
        finally:
            file_path = Path(mp3_output_path)
            file_path.unlink(missing_ok=True)
            print(f"{mp3_output_path} deleted from local instance")

    return save_status