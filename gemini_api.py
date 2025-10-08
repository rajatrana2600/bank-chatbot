import google.generativeai as genai
import streamlit as st
import os

GEMINI_MODEL = "gemini-2.5-flash"

# Default generation config
GENERATION_CONFIG = genai.types.GenerationConfig(
  temperature=0.4,
  top_p=0.92,
  top_k=40,
  max_output_tokens=2500
)

# Cache for prompt template
_PROMPT_TEMPLATE = None

def get_prompt_template():
    """Get cached prompt template or load it if not cached"""
    global _PROMPT_TEMPLATE
    if _PROMPT_TEMPLATE is None:
        prompt_path = os.path.join('resources', 'detailed_prompt_template.txt')
        with open(prompt_path, 'r') as f:
            _PROMPT_TEMPLATE = f.read()
    return _PROMPT_TEMPLATE

def get_gemini_response(query, context, history):
    """
    Get a response from the Gemini API with conversation history.

    Args:
        query (str): The current user query
        context (str): The context from knowledge base or policy documents
        history (list): Previous conversation history

    Returns:
        str: The generated response
    """
    # Process history more efficiently by limiting size upfront
    recent_history = history[-8:] if len(history) > 8 else history
    
    # Pre-calculate role strings to avoid repeated string operations
    history_text = []
    for msg in recent_history:
        role = "User" if msg['role'] == 'user' else "Assistant"
        history_text.append(f"{role}: {msg['content']}")
    history_text = "\n".join(history_text)

    # Get cached prompt template
    prompt_template = get_prompt_template()
    
    # Format prompt with dynamic values
    prompt = prompt_template.format(
        history_text=history_text,
        query=query,
        context=context
    )

    try:
        # Initialize model with config if not already done
        if 'gemini_model' not in st.session_state:
            model = genai.GenerativeModel(GEMINI_MODEL)
            # Store both model and its config in session state
            st.session_state.gemini_model = model
            st.session_state.generation_config = GENERATION_CONFIG

        # Use cached model instance with stored config
        response = st.session_state.gemini_model.generate_content(
            prompt,
            generation_config=st.session_state.generation_config
        )
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini API failed: {e}")
        return f"Error getting response from Gemini: {str(e)}"

def initialize_gemini_api(api_key):
  """Initialize the Gemini API with the provided key"""
  if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
  genai.configure(api_key=api_key)
