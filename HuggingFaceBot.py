import wikipedia
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

# --- 1. Download & Prepare Wikipedia Pages ---
related_articles = [
    "United States",
    "History of the United States",
    "Economy of the United States",
    "U.S. Constitution",
    "Politics of the United States",
    "Foreign relations of the United States",
    "Demographics of the United States",
    "Culture of the United States",
    "Education in the United States",
]

print("📥 Downloading Wikipedia articles...")
all_texts = []
for title in related_articles:
    try:
        page = wikipedia.page(title)
        all_texts.append(page.content)
        print(f"✔️ Fetched: {title}")
    except Exception as e:
        print(f"❌ Failed to fetch {title}: {e}")

# --- 2. Chunk the Documents ---
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
documents = splitter.create_documents(all_texts)

# --- 3. Generate Embeddings (Locally) ---
print("🔍 Embedding with HuggingFace...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embeddings)

# --- 4. Load a Local LLM ---
print("🧠 Loading local Hugging Face model...")
llm_pipeline = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Small and fast
    tokenizer="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    max_new_tokens=256,
    temperature=0.7,
    do_sample=True
)
llm = HuggingFacePipeline(pipeline=llm_pipeline)

# --- 5. Build RAG Chain ---
retriever = db.as_retriever(search_type="similarity", k=4)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
)

# --- 6. Ask Questions ---
print("\n✅ Fully local RAG system ready! Ask anything about the United States.")
print("Type 'exit' to quit.\n")

while True:
    query = input("You: ")
    if query.strip().lower() in {"exit", "quit"}:
        break
    result = qa({"query": query}) 
    # print("\nAnswer:\n", result["result"], "\n")