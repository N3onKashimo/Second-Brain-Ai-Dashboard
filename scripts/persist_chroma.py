# persist_chroma.py
import os, json
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

def load_docs(logs_dir="..\\logs"):
    docs = []
    for fn in os.listdir(logs_dir):
        if fn.endswith((".json", ".md", ".txt")):
            path = os.path.join(logs_dir, fn)
            if fn.endswith(".json"):
                msgs = json.load(open(path))
                text = "\n".join(f"{m['role']}: {m['content']}" for m in msgs)
            else:
                text = open(path, encoding="utf-8").read()
            docs.append(Document(page_content=text, metadata={"source": fn}))
    return docs

if __name__ == "__main__":
    docs = load_docs()
    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectordb = Chroma.from_documents(docs=docs, embedding_function=emb, persist_directory="../chroma_db")
    vectordb.persist()
    print(f"✅ Persisted {len(docs)} docs.")
