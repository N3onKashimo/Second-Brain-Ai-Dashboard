# memory_retriever.py

from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# === Configure Paths ===
persist_dir = "F:/OllamaModels/memory/vectorstore/"
collection_name = "chatgpt-index"

# === Connect to Chroma vector store ===
chroma_client = chromadb.PersistentClient(path=persist_dir)
chroma_collection = chroma_client.get_or_create_collection(collection_name)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# === Load embedding model ===
embed_model = HuggingFaceEmbedding(
    model_name="nomic-ai/nomic-embed-text-v1",
    trust_remote_code=True
)

# === Rebuild index from storage ===
storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
index = load_index_from_storage(
    storage_context=storage_context,
    embed_model=embed_model,
    vector_store=vector_store
)

# === Create retriever query engine ===
query_engine = RetrieverQueryEngine.from_index(index)

# === Example CLI usage ===
if __name__ == "__main__":
    while True:
        query = input("\n🔍 Ask your memory: ")
        if query.lower() in {"exit", "quit"}:
            break

        response = query_engine.query(query)
        print("\n🧠 Memory says:\n", str(response))
