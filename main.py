import sqlite3
from semantic_search import search
from local_llm import generate_response

def fetch_submission_by_id(submission_id):
    conn = sqlite3.connect("TourOdishaAI/locinfo.db")
    c = conn.cursor()
    c.execute("""
        SELECT location, description, best_time, tips
        FROM submissions
        WHERE id=?
    """, (submission_id,))
    row = c.fetchone()
    conn.close()
    return row

def build_context(submission_ids):
    blocks = []
    for sid in submission_ids:
        row = fetch_submission_by_id(sid)
        if row:
            loc, desc, bt, tips = row
            blocks.append(
                f"Location: {loc}\nDescription: {desc}\nBest time: {bt}\nTips: {tips}"
            )
    return "\n\n".join(blocks)

def chat(query):
    submission_ids = search(query, top_k=3)
    context = build_context(submission_ids)
    prompt = (
        "You are a helpful tour agent for Odisha. Use the following community submissions to answer the user's question.\n\n"
        f"{context}\n\n"
        f"User: {query}\nTour Agent:"
    )
    response = generate_response(prompt)
    print("\n" + "-"*60)
    print(response)
    print("-"*60 + "\n")
