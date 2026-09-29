import os

from dotenv import load_dotenv
import google.generativeai as genai
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = os.getenv("BANK_ID", "editorial-brain")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
BRAND_VOICE_SYSTEM_PROMPT = (
    "You are a content strategist for a B2B SaaS company that sells "
    "project management software. You have access to the team's real "
    "publishing history, performance results, and editorial feedback, "
    "provided to you as relevant history below.\n\n"
    "Rules:\n"
    "- Ground every recommendation in the history you're given. If you "
    "reference a past post, cite its title and what happened with it.\n"
    "- If the history shows a format or topic underperforming, say so "
    "directly and explain why, based on the notes in the history.\n"
    "- If the history mentions topics that were never covered, treat "
    "those as real opportunities, not filler suggestions.\n"
    "- Follow any brand-voice feedback in the history.\n"
    "- If the history given to you is empty or unrelated to the request, "
    "say so plainly and give a generic best-practice answer instead of "
    "inventing history that wasn't provided.\n"
    "- Be concise and specific. No hype, no buzzwords.\n"
)


def get_hindsight_client():
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )


def recall_context(request, bank_id=None, limit=10):
    client = get_hindsight_client()
    result = client.recall(bank_id=bank_id or BANK_ID, query=request)

    memories = getattr(result, "results", result)

    lines = []
    for m in memories[:limit]:
        text = getattr(m, "text", None) or getattr(m, "content", None) or str(m)
        lines.append("- " + text)

    return "\n".join(lines) if lines else "(no relevant memory found)"


def generate_with_retry(prompt, max_retries=3):
    model = genai.GenerativeModel(MODEL_NAME)
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)
            if response.text and response.text.strip():
                return response.text
            raise ValueError("Model returned an empty response.")
        except Exception as e:
            last_error = e
            print("  [attempt " + str(attempt) + "] generation failed (" + str(e) + "); retrying")

    raise RuntimeError("Generation failed after " + str(max_retries) + " attempts: " + str(last_error))


def advise(request, bank_id=None):
    context = recall_context(request, bank_id=bank_id)

    prompt = BRAND_VOICE_SYSTEM_PROMPT + "\n\nRelevant history from our content memory:\n" + context + "\n\nRequest: " + request

    answer = generate_with_retry(prompt)
    return answer, context


if __name__ == "__main__":
    import sys

    request = " ".join(sys.argv[1:]) or "Give me three blog topics for next month"
    print("Request: " + request + "\n")

    answer, context = advise(request)

    print("--- Recalled context ---")
    print(context)
    print("\n--- Agent answer ---")
    print(answer)