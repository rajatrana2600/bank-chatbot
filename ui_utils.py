import streamlit as st

@st.cache_data
def load_css():
  """Load and cache CSS styles"""
  try:
    with open("resources/styles.css") as f:
      return f.read()
  except Exception as e:
    print(f"[ERROR] Failed to load CSS: {e}")
    return ""

def setup_ui():
  """Configure the UI components"""
  # Configure page with minimal settings
  st.set_page_config(
    page_title="Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar for faster loading
  )

  # Apply cached CSS
  st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

  # Header section
  st.markdown("<h1 class='header-title'>🏦 Banking Assistant</h1>", unsafe_allow_html=True)
  st.markdown("<p class='header-subtitle'>Ask questions about accounts, cards, loans, insurance, or investments. Also support exchange rate queries.</p>", unsafe_allow_html=True)

def display_chat_history():
  """Display the chat message history"""
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Add space at bottom for fixed input
  st.markdown("<br><br><br><br>", unsafe_allow_html=True)
