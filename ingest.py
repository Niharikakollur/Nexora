"""
ingest.py

Loads data/posts.json into your Hindsight memory bank.
"""

import json
import os
import time

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = os.getenv("BANK_ID", "editorial-brain")


def get_client():
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )


def post_to_text(post):
    read_min = post["avg_read_time_seconds"] // 60
    read_sec = post["avg_read_time_seconds"] % 60

    text = (
        f"Published '{post['title']}' on {post['date']}. "
        f"Topic: {post['topic']}. Format: {post['format']}. "
        f"Word count: {post['word_count']}. "
        f"Results after 30 days: {post['views_30d']} views, "
        f"{read_min}m {read_sec}s average read time, "
        f"{post['signups_30d']} signups."
    )

    if post.get("why"):
        text += f" Why it performed this way: {post['why']}"

    return text


def ingest_all(delay_seconds=0.0):
    client = get_client()

    with open("data/posts.json") as f:
        data = json.load(f)

    total = len(data["posts"]) + len(data["feedback"]) + 1
    done = 0

    print("Ingesting " + str(total) + " items into bank '" + BANK_ID + "'...")

    for post in data["posts"]:
        text = post_to_text(post)
        client.retain(bank_id=BANK_ID, content=text)
        done += 1
        print("  [" + str(done) + "/" + str(total) + "] retained " + post["id"])
        if delay_seconds:
            time.sleep(delay_seconds)

    for item in data["feedback"]:
        client.retain(bank_id=BANK_ID, content=item["text"])
        done += 1
        print("  [" + str(done) + "/" + str(total) + "] retained " + item["id"])
        if delay_seconds:
            time.sleep(delay_seconds)

    client.retain(bank_id=BANK_ID, content=data["gap_note"]["text"])
    done += 1
    print("  [" + str(done) + "/" + str(total) + "] retained gap note")

    print("Done. Check the Hindsight dashboard's Memories tab to confirm.")


def retain_post_mortem(post_id, result_summary, reason, bank_id=None):
    client = get_client()
    text = "Post-mortem for " + post_id + ": " + result_summary + ". Why it performed this way: " + reason
    client.retain(bank_id=bank_id or BANK_ID, content=text)
    print("Retained post-mortem for " + post_id)


def retain_feedback(text, bank_id=None):
    client = get_client()
    full_text = "Editorial feedback from the content lead: " + text
    client.retain(bank_id=bank_id or BANK_ID, content=full_text)
    print("Retained feedback.")


if __name__ == "__main__":
    ingest_all()