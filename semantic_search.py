import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DB_PATH = "TourOdishaAI/locinfo.db"
INDEX_PATH = "TourOdishaAI/faiss.index"
IDS_PATH = "TourOdishaAI/ids.npy"

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def fetch_submission_texts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id,
               location || '. ' || description || ' Best time: ' || best_time || '. Tips: ' || tips
        FROM submissions
    """)
    rows = c.fetchall()
    conn.close()
    return rows  # [(id, text), ...]

def build_index():
    rows = fetch_submission_texts()
    if not rows:
        print("No submissions found.")
        return
    ids, texts = zip(*rows)
    embeddings = model.encode(list(texts), convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, INDEX_PATH)
    np.save(IDS_PATH, np.array(ids))
    print(f"Indexed {len(ids)} submissions.")

def search(query, top_k=3):
    index = faiss.read_index(INDEX_PATH)
    ids = np.load(IDS_PATH)
    q_vec = model.encode([query], convert_to_numpy=True).astype(np.float32)
    D, I = index.search(q_vec, top_k)
    results = []
    for idx in I[0]:
        sub_id = int(ids[idx])
        results.append(sub_id)
    return results
