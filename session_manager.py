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
      api_key='ck-57TZ7sdbCW8oK9Jr7Q3awjFZ3UXrvN63RVfnNskBo4Ap',
      tenant='4382d23a-34eb-4a25-a0ba-1fcbc386a585',
      database='bank-chatbot'
    )
    # Get the existing collection (assumes it already exists)
    collection = client.get_collection(name="knowledge_base")
    st.session_state.collection = collection
    print(f"[INFO] Connected to existing Chroma collection with {collection.count()} entries")

  except Exception as e:
    print(f"[ERROR] Connecting to ChromaDB: {e}")
    st.error(f"Error connecting to ChromaDB: {str(e)}. Please run the populate_db.py script first to create the knowledge base.")
