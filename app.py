"""
app.py

Streamlit UI for the content strategy agent. Shows:
  - a chat box to ask for content advice
  - a side panel showing exactly what memory was recalled for that
    request (this is the part that makes memory visible to judges)
  - a box to log editorial feedback
  - a form to log a post's real results after 30 days (the
    post-mortem loop)

Run with:
    streamlit run app.py
"""

import streamlit as st

from agent import advise
from ingest import retain_feedback, retain_post_mortem

st.set_page_config(page_title="Editorial Brain", page_icon="🧠", layout="wide")

st.title("🧠 Editorial Brain")
st.caption("A content strategy agent that remembers what we've published, "
           "what worked, and what didn't -- powered by Hindsight memory.")

col_chat, col_memory = st.columns([2, 1])

if "history" not in st.session_state:
    st.session_state.history = []

with col_chat:
    st.subheader("Ask for content strategy advice")
    request = st.text_area(
        "What do you need?",
        placeholder="e.g. Give me three blog topics for next month",
        height=80,
    )

    if st.button("Ask", type="primary") and request.strip():
        with st.spinner("Recalling history and generating advice..."):
            try:
                answer, context = advise(request)
                st.session_state.history.append(
                    {"request": request, "answer": answer, "context": context}
                )
            except Exception as e:  # noqa: BLE001
                st.error(f"Something went wrong: {e}")

    for item in reversed(st.session_state.history):
        st.markdown(f"**You:** {item['request']}")
        st.markdown(item["answer"])
        with st.expander("What memory did the agent recall for this?"):
            st.text(item["context"])
        st.divider()

with col_memory:
    st.subheader("Teach the agent")

    st.markdown("**Give editorial feedback**")
    feedback_text = st.text_input(
        "e.g. That draft was too salesy",
        key="feedback_input",
    )
    if st.button("Save feedback") and feedback_text.strip():
        retain_feedback(feedback_text)
        st.success("Feedback saved to memory.")

    st.markdown("---")

    st.markdown("**Log a post-mortem**")
    pm_post_id = st.text_input("Post ID or title", key="pm_id")
    pm_result = st.text_input(
        "Results (e.g. 1,200 views, 15 signups)", key="pm_result"
    )
    pm_reason = st.text_input(
        "Why it performed this way", key="pm_reason"
    )
    if st.button("Save post-mortem") and pm_post_id and pm_result and pm_reason:
        retain_post_mortem(pm_post_id, pm_result, pm_reason)
        st.success("Post-mortem saved to memory.")

st.markdown("---")
st.caption(
    "Tip for a demo: ask the same question before and after loading data "
    "(via ingest.py) to show the agent's answers change once it has real "
    "history to recall from."
)
