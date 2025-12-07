import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import streamlit as st

def process_and_populate_collection():
  # Connect to ChromaDB client
  client = chromadb.CloudClient(
    api_key='ck-57TZ7sdbCW8oK9Jr7Q3awjFZ3UXrvN63RVfnNskBo4Ap',
    tenant='4382d23a-34eb-4a25-a0ba-1fcbc386a585',
    database='bank-chatbot'
  )
  # Check if collection exists, if yes, delete it
  try:
    client.delete_collection(name="knowledge_base")
    print("[INFO] Deleted existing collection")
  except Exception:
    print("[INFO] No existing collection found")

  # Create a new collection
  collection = client.create_collection(
    name="knowledge_base",
    metadata={"description": "BC Bank FAQ Knowledge Base"}
  )

  # Load the model
  model = SentenceTransformer("all-MiniLM-L6-v2")

  # Process all Excel files
  excel_files = [
     "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part1.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part2.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part3.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part4.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part5.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part6.csv",
    "C:/Users/Dell/Downloads/knowledge_base/BankFAQs_Part7.csv"
  ]

  for file in excel_files:
    print(f"[INFO] Processing {file}...")
    df = pd.read_csv(file)
    embeddings = model.encode(df["Question"].astype(str).tolist(), show_progress_bar=True)
    ids = df["Serial"].astype(str).tolist()
    metadatas = df[["Serial", "Question", "Class"]].to_dict(orient="records")
    documents = df["Answer"].astype(str).tolist()
    collection.add(ids=ids, embeddings=embeddings.tolist(), metadatas=metadatas, documents=documents)

  print("[INFO] ✅ All CSV files added to ChromaDB")
  print(f"[INFO] Collection 'knowledge_base' created with {collection.count()} entries")

if __name__ == "__main__":
  print("[INFO] Starting to populate ChromaDB with bank FAQ data...")
  process_and_populate_collection()
