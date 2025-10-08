import os
import streamlit as st
from gemini_api import initialize_gemini_api
from query_processor import process_query
from session_manager import initialize_session_state
from ui_utils import setup_ui, display_chat_history

def main():
  """Main application entry point"""
  # Initialize session state first
  initialize_session_state()

  # Set up the UI components
  setup_ui()

  # Check API key once at startup
  try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    initialize_gemini_api(GEMINI_API_KEY)
  except ValueError as e:
    st.error(str(e))
    return

  # Display chat history
  display_chat_history()

  # Chat input
  user_query = st.chat_input("Ask a question...")

  # Process queries
  if user_query:
    process_query(user_query)

if __name__ == "__main__":
  main()
