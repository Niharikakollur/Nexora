# Editorial Brain

A content strategy agent that remembers what a team has published,
what performed well, what didn't, and why — powered by
[Hindsight](https://github.com/vectorize-io/hindsight) persistent
agent memory.

## The problem

Content teams re-plan from scratch every cycle because their
publishing history lives in spreadsheets, dashboards, and people's
heads. Generic AI writing tools make it worse: they have no memory
of what a team has already published, so they suggest the same
generic topics to every company, every time.

## What this agent does

- **Remembers every post**: topic, format, date, and 30-day
  performance results.
- **Learns from post-mortems**: after results come in, it retains
  *why* a post performed the way it did, not just the numbers.
- **Remembers editorial feedback**: corrections like "too salesy"
  shape future recommendations.
- **Recalls before it answers**: every request is grounded in the
  team's real history, not a generic prompt.

## How it works

1. `generate_data.py` creates a synthetic 40-post backlog with
   deliberate patterns (teardown/case-study formats outperform
   listicles/definitions; onboarding content drives signups; a few
   topics have never been covered).
2. `ingest.py` retains each post, feedback item, and gap note into a
   Hindsight memory bank as plain-language facts.
3. `agent.py` recalls relevant memory for a request, then generates
   a grounded answer with an LLM (via Groq), with retry handling for
   malformed model responses.
4. `app.py` is a Streamlit UI with a visible "what memory was
   recalled" panel, an editorial-feedback box, and a post-mortem
   logging form.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then fill in .env with your real Hindsight and Groq keys
```

Create a memory bank named `editorial-brain` in
[Hindsight Cloud](https://ui.hindsight.vectorize.io) (or your
self-hosted instance), then:

```bash
python generate_data.py   # creates data/posts.json
python ingest.py          # loads it into Hindsight
python agent.py "Give me three blog topics for next month"
streamlit run app.py      # full UI
```

## Demonstrating memory (the before/after)

Ask the agent the same question at three points:

1. **Before ingest**: generic, could apply to any company.
2. **After `ingest.py`**: grounded in the real backlog — it cites
   specific past posts and results.
3. **After adding feedback and a post-mortem**: recommendations
   reflect brand voice and lessons from what didn't work.

## Built with

- [Hindsight](https://hindsight.vectorize.io/) for persistent agent
  memory
- [Groq](https://groq.com/) for fast LLM inference
  (`openai/gpt-oss-120b`)
- Streamlit for the UI
