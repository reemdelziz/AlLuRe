from flask import Flask, request, jsonify
from flask_cors import CORS

import pickle
import os

import wikipedia
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from langchain_core.documents import Document
from transformers import pipeline


def preprocess_lists(text):
    """
    Process raw text to preserve lists, paragraphs, and headings as separate chunks.
    """
    lines = text.split('\n')
    processed_chunks = []
    buffer = []

    for line in lines:
        stripped = line.strip()
        
        # Detect list items or headings
        is_list_item = stripped.startswith(("-", "*")) or stripped[:2].isdigit()
        is_heading = stripped.startswith("==") and stripped.endswith("==")

        if is_list_item or is_heading:
            if buffer:
                processed_chunks.append(" ".join(buffer))
                buffer = []
            processed_chunks.append(stripped)
        else:
            if stripped:  # Skip empty lines
                buffer.append(stripped)

    if buffer:
        processed_chunks.append(" ".join(buffer))

    return processed_chunks



# Set up Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend access


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
    "List of presidents of the United States",
]

# File where we cache the articles
wiki_cache_path = "wiki_texts.pkl"

if os.path.exists(wiki_cache_path):
    print("📂 Loading cached Wikipedia articles...")
    with open(wiki_cache_path, "rb") as f:
        all_texts = pickle.load(f)
else:
    print("📥 Downloading Wikipedia articles...")
    all_texts = []
    for title in related_articles:
        try:
            page = wikipedia.page(title)
            all_texts.append(page.content)
            print(f"✔️ Fetched: {title}")
        except Exception as e:
            print(f"❌ Failed to fetch {title}: {e}")

    # Save the result
    with open(wiki_cache_path, "wb") as f:
        pickle.dump(all_texts, f)
    print(f"✅ Saved articles to {wiki_cache_path}")

# Preprocess to preserve lists
print("🧹 Preprocessing Wikipedia articles to preserve lists...")

all_chunks = []
for text in all_texts:
    processed = preprocess_lists(text)
    all_chunks.extend(processed)

print(f"🧩 Total processed chunks: {len(all_chunks)}")

# Now do intelligent chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)

documents = splitter.create_documents(all_chunks)

print(f"📄 Total documents created: {len(documents)}")

# OLD SPLITTING CODE
# splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ".", " "])
# documents = splitter.create_documents(all_texts)

# TEST
for doc in documents:
    if "president" in doc.page_content.lower():
        print(doc.page_content)
        break


print("🔍 Embedding with HuggingFace...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_documents(documents, embeddings)

print("🧠 Loading local Hugging Face model...")
llm_pipeline = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    tokenizer="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    max_new_tokens=256,
    temperature=0.7,
    do_sample=True
)
llm = HuggingFacePipeline(pipeline=llm_pipeline)

numSources = 4
retriever = db.as_retriever(search_type="similarity", k=numSources)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    query = data.get('question', '').strip()
    if not query:
        return jsonify({"error": "No question provided"}), 400
    
    query_vector = embeddings.embed_query(query)
    results_with_scores = db.similarity_search_with_score_by_vector(query_vector, k=numSources)
    
    # CALCULATING CONFIDENCE LEVELS
    similarities = [1 / (1 + score) for _, score in results_with_scores]
    avg_similarity = sum(similarities) / len(similarities)

    print(f"🔎 Avg similarity: {avg_similarity:.3f}")
    
    # docs = [doc for doc, _ in results_with_scores]
    # retriever = FAISS.from_documents(docs, embeddings).as_retriever(search_type="similarity", k=numSources)
    # qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)


    result = qa({"query": query})
    raw_ans = result["result"]

    # Parse answer
    if "Helpful Answer:" in raw_ans:
        ans = raw_ans.split("Helpful Answer:")[-1].strip()
    else:
        ans = raw_ans.strip()
    
    sources = []
    parsed = result["result"].split('\n\n')
    for i in range(1, min(numSources+1, len(parsed))):
        sources.append(parsed[i])

    # print(sources)

    # FILTERING FOR HIGH CONFIDENCE
    CONFIDENCE_THRESHOLD = 0.5
    if avg_similarity < CONFIDENCE_THRESHOLD:
        ans = "🤔 I'm not confident enough in the answer. Please provide documentation or rephrase the question. Check the sources I found for related information."
    
    return jsonify({
        "answer": ans,
        "sources": sources,
        "confidence": float(round(avg_similarity, 3))
    })

if __name__ == '__main__':
    app.run(debug=True)


# USER SUBMITTED SOURCE
@app.route('/submit', methods=['POST'])
def submit_fact():
    data = request.get_json()
    fact = data.get("fact", "").strip()
    source = data.get("source", "User Submission").strip()

    if not fact:
        return jsonify({"error": "No fact provided"}), 400

    # Create Document object
    new_doc = Document(page_content=fact, metadata={"source": source})

    # Embed and add to FAISS
    db.add_documents([new_doc])
    print(f"➕ Added new fact: {fact[:60]}...")

    return jsonify({"message": "Fact added successfully"})