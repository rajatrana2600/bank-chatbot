import chromadb
import streamlit as st

def initialize_session_state():
  """Initialize session state variables and connections"""
  # Initialize chat message history with welcome message
  if 'messages' not in st.session_state:
    st.session_state.messages = [
      {"role": "assistant", "content": "👋 Welcome to BC Bank Chatbot!"}
    ]

  # Connect to ChromaDB collection
  if 'collection' not in st.session_state:
    connect_to_chromadb()

def connect_to_chromadb():
  """Connect to the ChromaDB collection"""
  try:
    # Connect to ChromaDB client
    client = chromadb.CloudClient(
      api_key='ck-7bD95NuNebzB4NuD8goHvnDrt1GCqfKEbghob6bkRRMS',
      tenant='f780702a-cea3-4602-b65f-e7f41f6546ec',
      database='my-project'
    )

    # Get the existing collection (assumes it already exists)
    collection = client.get_collection(name="knowledge_base")
    st.session_state.collection = collection
    print(f"[INFO] Connected to existing Chroma collection with {collection.count()} entries")

  except Exception as e:
    print(f"[ERROR] Connecting to ChromaDB: {e}")
    st.error(f"Error connecting to ChromaDB: {str(e)}. Please run the populate_db.py script first to create the knowledge base.")
