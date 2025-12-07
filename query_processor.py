import streamlit as st
import random
import json
import os
from gemini_api import get_gemini_response

# Load categories from JSON file and create optimized lookup
def load_categories():
    categories_path = os.path.join('resources', 'categories.json')
    with open(categories_path, 'r') as f:
        categories_dict = json.load(f)

    keyword_map = {}
    for category, keywords in categories_dict.items():
        for keyword in keywords:
            keyword_map[keyword.lower()] = category
    return categories_dict, keyword_map

# Load categories and keyword map at module level
categories, keyword_map = load_categories()

def process_query(user_query):
  """
  Process user query and generate a response.

  Args:
      user_query (str): The user's query
  """
  # Add user message to history
  st.session_state.messages.append({"role": "user", "content": user_query})
  with st.chat_message("user"):
    st.markdown(user_query)

  with st.chat_message("assistant"):
    response_placeholder = st.empty()

    # List of random loading messages
    loading_messages = [
      "Please hold on while I prepare the most accurate information for you.",
      "Just a moment, I'm gathering the details for your request.",
      "I'm checking the latest information to give you the best answer.",
      "Working on your request, this will only take a few seconds…",
      "Let me review your query and provide the right details shortly.",
      "One moment, I'm putting together the information you need.",
      "Retrieving the details for you, please hold on."
    ]

    # Use the spinner only for the processing part
    with st.spinner(random.choice(loading_messages)):
      response = generate_response(user_query)

    # Display response after spinner is complete
    response_placeholder.markdown(response)

    # Add to history
    st.session_state.messages.append({"role": "assistant", "content": response})

def generate_response(user_query):
  """
  Generate a response based on the user query

  Args:
      user_query (str): The user's query

  Returns:
      str: The generated response
  """
  user_query_lower = user_query.lower().strip()

  # Enhanced follow-up detection
  followup_phrases = {
    "yes", "sure", "ok", "okay", "please", "right", "yeah", "yep", "alright", "fine", "sounds good",
    "got it", "understood", "i see", "what do you mean", "can you clarify", "clarify",
    "and", "what about", "how about", "what else", "then what", "next", "and then", "keep going",
    "tell me more", "continue", "go on", "proceed", "elaborate", "explain further",
    "can you explain", "give me more details", "give me details", "expand on that", "more info", "say more"
  }

  # Check if this is a follow-up query
  is_followup = False
  search_query = user_query
  
  if len(st.session_state.messages) >= 3:
    # Check for simple follow-up phrases
    if user_query_lower in followup_phrases or any(phrase in user_query_lower for phrase in followup_phrases):
      is_followup = True
      search_query = st.session_state.messages[-3]["content"]
    
    # Check for pronouns referring to previous context
    pronouns = {"it", "this", "that", "these", "those", "they", "them"}
    if any(pronoun in user_query_lower.split() for pronoun in pronouns):
      is_followup = True
      # Combine previous query with current for better context
      search_query = f"{st.session_state.messages[-3]['content']} {user_query}"
    
    # Check for questions starting with conjunctions
    if any(user_query_lower.startswith(word) for word in ["and ", "but ", "or ", "so "]):
      is_followup = True
      # Combine previous query with current for better context
      search_query = f"{st.session_state.messages[-3]['content']} {user_query}"

  # Check if query matches any category for metadata filtering
  search_query_lower = search_query.lower()

  # Use optimized keyword lookup
  matching_category = None
  for word in search_query_lower.split():
    if word in keyword_map:
      matching_category = keyword_map[word]
      break

  # Cache key for query results
  cache_key = f"{search_query}_{matching_category}"
  
  # Check if results are in cache
  if 'query_cache' not in st.session_state:
    st.session_state.query_cache = {}
    
  if cache_key in st.session_state.query_cache:
    results = st.session_state.query_cache[cache_key]
  else:
    # Perform standard retrieval - with category filter if available
    if matching_category:
      # Use metadata filter with matching category
      results = st.session_state.collection.query(
        query_texts=[search_query],
        n_results=5,
        where={"Class": matching_category}
      )
    else:
      # No category match, do general search
      results = st.session_state.collection.query(
        query_texts=[search_query],
        n_results=5
      )
    
    # Cache the results
    st.session_state.query_cache[cache_key] = results
    
    # Limit cache size to prevent memory issues
    if len(st.session_state.query_cache) > 100:
      # Remove oldest entries
      oldest_keys = list(st.session_state.query_cache.keys())[:50]
      for key in oldest_keys:
        del st.session_state.query_cache[key]

  documents = results.get('documents', [[]])[0]
  distances = results.get('distances', [[]])[0]

  # Determine if we have sufficient context
  if documents and any(dist <= 0.8 for dist in distances):
    # Format context from the retrieved documents
    kb_context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
    return get_gemini_response(user_query, kb_context, st.session_state.messages)
  else:
    # No relevant information found in knowledge base
    return "Could you please clarify what you mean? I'll be able to help you better with a little more detail or call Customer support at +91-9876543210"
