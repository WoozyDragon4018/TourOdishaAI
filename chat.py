# run_chat.py
from main import chat

while True:
    q = input("Ask your tour question: ")
    if q.lower() in ["exit", "quit"]:
        break
    chat(q)
