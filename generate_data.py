"""
generate_data.py

Creates a synthetic backlog of blog posts for a fictional B2B SaaS
company (project management software). The data has deliberate
patterns built in so the content strategy agent has real signal to
learn from:

  - "teardown" and "case_study" formats consistently outperform
    "listicle" and "definition" formats
  - onboarding-related topics drive the most signups
  - three topics have NEVER been covered (a gap for the agent to find)
  - a handful of posts include a human-written "why" explanation,
    simulating an editorial post-mortem

Run this once to produce data/posts.json, which ingest.py then
loads into Hindsight.
"""

import json
import random
from datetime import date, timedelta

random.seed(42)

FORMATS_GOOD = ["teardown", "case_study"]
FORMATS_BAD = ["listicle", "definition"]
FORMATS_NEUTRAL = ["how_to", "opinion"]

TOPICS_COVERED = [
    "employee onboarding",
    "remote team rituals",
    "meeting efficiency",
    "team communication",
    "pricing pages",
    "product basics",
    "hiring for startups",
    "async work",
    "sprint planning",
    "customer churn",
]

# Deliberately left out of the backlog so the agent can identify a gap.
TOPICS_NEVER_COVERED = [
    "security and compliance",
    "integrations with other tools",
    "customer success stories",
]

TITLE_TEMPLATES = {
    "teardown": [
        "Teardown: How {company} Cut {metric} by Half",
        "What Changed When {company} Rebuilt Their {topic} Process",
    ],
    "case_study": [
        "How {company} Solved Their {topic} Problem",
        "Inside {company}'s {topic} Overhaul",
    ],
    "listicle": [
        "{n} Tips for Better {topic}",
        "{n} Mistakes Teams Make with {topic}",
    ],
    "definition": [
        "What Is {topic}? A Complete Guide",
        "{topic}: Definitions and Best Practices",
    ],
    "how_to": [
        "A Practical Guide to {topic}",
        "How to Actually Improve {topic}",
    ],
    "opinion": [
        "Why We Changed Our Approach to {topic}",
        "The Problem with How Most Teams Handle {topic}",
    ],
}

COMPANIES = ["a 20-person agency", "a Series A startup", "a remote-first team",
             "a 200-person engineering org", "a fast-growing sales team"]
METRICS = ["meeting time", "onboarding time", "response time", "handoff delays"]

REASON_GOOD = [
    "It opened with a concrete, specific problem instead of a generic definition, "
    "and included real numbers from the featured team.",
    "The first-person, specific-numbers format held attention much longer than "
    "our usual explainer style.",
    "Readers responded well to seeing a real team's before-and-after, rather than "
    "abstract advice.",
]
REASON_BAD = [
    "The introduction was a generic definition that readers likely already knew, "
    "so they bounced before reaching the useful part.",
    "This format has consistently had low read time for our audience; it reads "
    "as filler rather than a real answer.",
    "It led with a listicle format, which tends to get skimmed rather than read "
    "in full.",
]


def make_post(i, pub_date, topic, fmt):
    template = random.choice(TITLE_TEMPLATES[fmt])
    title = template.format(
        company=random.choice(COMPANIES).title(),
        topic=topic.title(),
        metric=random.choice(METRICS),
        n=random.choice([3, 5, 7]),
    )

    is_onboarding = "onboarding" in topic
    if fmt in FORMATS_GOOD:
        base_views = random.randint(3500, 5500)
        base_read = random.randint(230, 330)  # seconds
        base_signups = random.randint(200, 420)
        reason = random.choice(REASON_GOOD)
    elif fmt in FORMATS_BAD:
        base_views = random.randint(900, 2000)
        base_read = random.randint(40, 90)
        base_signups = random.randint(8, 35)
        reason = random.choice(REASON_BAD)
    else:
        base_views = random.randint(1800, 3200)
        base_read = random.randint(90, 180)
        base_signups = random.randint(40, 120)
        reason = None

    if is_onboarding:
        base_signups = int(base_signups * 1.4)

    include_reason = reason is not None and random.random() < 0.7

    return {
        "id": f"post-{i:03d}",
        "title": title,
        "date": pub_date.isoformat(),
        "topic": topic,
        "format": fmt,
        "word_count": random.randint(800, 1900),
        "views_30d": base_views,
        "avg_read_time_seconds": base_read,
        "signups_30d": base_signups,
        "why": reason if include_reason else None,
    }


def generate(n_posts=40):
    posts = []
    start = date(2026, 1, 6)
    current = start

    all_formats = FORMATS_GOOD * 3 + FORMATS_BAD * 3 + FORMATS_NEUTRAL * 2

    for i in range(1, n_posts + 1):
        topic = random.choice(TOPICS_COVERED)
        fmt = random.choice(all_formats)
        current += timedelta(days=random.randint(5, 9))
        posts.append(make_post(i, current, topic, fmt))

    return posts


def make_feedback():
    """Simulated editorial / brand-voice feedback, retained separately."""
    return [
        {
            "id": "feedback-001",
            "date": "2026-04-08",
            "text": (
                "Editorial feedback from the content lead: the draft on team "
                "communication was too salesy. Our brand voice is plain, "
                "practical, and direct. Avoid hype words and open with a real "
                "example instead of a definition."
            ),
        },
        {
            "id": "feedback-002",
            "date": "2026-06-02",
            "text": (
                "Editorial feedback from the content lead: readers respond well "
                "when posts include a specific team or company, even if "
                "anonymized. Keep using named-but-anonymized examples."
            ),
        },
    ]


def make_gap_note():
    return {
        "id": "gap-note-001",
        "date": date.today().isoformat(),
        "text": (
            "Topics we have never covered on the blog: "
            + ", ".join(TOPICS_NEVER_COVERED)
            + ". These are candidate topics for future content."
        ),
    }


if __name__ == "__main__":
    posts = generate(40)
    feedback = make_feedback()
    gap_note = make_gap_note()

    output = {
        "posts": posts,
        "feedback": feedback,
        "gap_note": gap_note,
    }

    with open("data/posts.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(posts)} posts, {len(feedback)} feedback items, "
          f"and 1 gap note -> data/posts.json")
