import re
import pandas as pd
import chromadb
import networkx as nx
import spacy
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Tuple
import base64
import io

# Initialize spaCy and embedding model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️ spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Initialize ChromaDB
chroma = chromadb.Client()
COLLECTION_NAME = "study_chunks"

def get_or_create_collection():
    """Get existing collection or create new one"""
    try:
        collection = chroma.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    except:
        try:
            chroma.delete_collection(COLLECTION_NAME)
        except:
            pass
        collection = chroma.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    return collection

def split_text(text: str, chunk_size: int = 400) -> List[str]:
    """Split text into chunks of specified size"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def store_chunks(text: str) -> List[str]:
    """Store text chunks in ChromaDB"""
    chunks = split_text(text)
    collection = get_or_create_collection()
    
    # Generate unique IDs
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    # Add to collection
    collection.add(documents=chunks, ids=ids, embeddings=embedding_fn(chunks))
    return chunks

def retrieve_chunks(question: str, k: int = 3) -> List[str]:
    """Retrieve relevant chunks for a question"""
    collection = get_or_create_collection()
    results = collection.query(query_texts=[question], n_results=k)
    return results['documents'][0]

def extract_concepts(text: str) -> List[Tuple[str, str, str]]:
    """Extract subject-verb-object relationships from text"""
    if not nlp:
        return []
    
    doc = nlp(text)
    concepts = []
    
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subj = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w.text for w in token.rights if w.dep_ in ("dobj", "pobj")]
                if subj and obj:
                    concepts.append((subj[0], token.text, obj[0]))
    
    return concepts

def build_graph(text: str) -> nx.DiGraph:
    """Build a directed graph from text concepts"""
    G = nx.DiGraph()
    for s, r, o in extract_concepts(text):
        G.add_edge(s, o, label=r)
    return G

def graph_context(question: str, G: nx.DiGraph) -> str:
    """Get graph context relevant to a question"""
    nodes = [n for n in G.nodes if question.lower() in n.lower()]
    info = []
    
    for node in nodes:
        for neighbor in G.neighbors(node):
            rel = G.edges[node, neighbor]['label']
            info.append(f"{node} --{rel}--> {neighbor}")
    
    return "\n".join(info)

def extract_questions_from_paper(paper_text: str) -> pd.DataFrame:
    """Extract questions from generated paper text"""
    pattern = r"\d+\.\s(.+?)\s*\((\d+)\s*marks?\)\s*Answer:\s*(.*?)(?=\n\d+\.|\Z)"
    matches = re.findall(pattern, paper_text, re.DOTALL)
    
    questions = []
    for q_text, marks, answer in matches:
        questions.append({
            "question_text": q_text.strip(),
            "marks": int(marks.strip()),
            "answer_text": answer.strip()
        })
    
    return pd.DataFrame(questions)

def decode_csv_content(base64_content: str) -> pd.DataFrame:
    """Decode base64 CSV content to DataFrame"""
    try:
        decoded_content = base64.b64decode(base64_content).decode('utf-8')
        return pd.read_csv(io.StringIO(decoded_content))
    except Exception as e:
        raise ValueError(f"Failed to decode CSV content: {str(e)}")

def encode_csv_content(df: pd.DataFrame) -> str:
    """Encode DataFrame to base64 CSV content"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    return base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

def calculate_percentage(score: float, max_marks: float) -> float:
    """Calculate percentage score"""
    return (score / max_marks) * 100 if max_marks > 0 else 0 