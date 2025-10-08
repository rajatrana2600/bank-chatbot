import requests
import re
import json

def get_currency_map():
    """Load currency mappings"""
    try:
        with open('resources/exchange_rate_mapping.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load currency mappings: {e}")
        return {}

def get_exchange_rates():
    """Get current exchange rates"""
    try:
        api_url = "https://v6.exchangerate-api.com/v6/1132ea8d26455cd85dfe935e/latest/USD"
        response = requests.get(api_url)
        data = response.json()
        return data["conversion_rates"] if data["result"] == "success" else None
    except Exception as e:
        print(f"[ERROR] Exchange rate API failed: {e}")
        return None

def find_currencies_in_query(query, valid_currencies):
    """Extract currency codes from query"""
    query_upper = query.upper()
    currencies = []
    
    # Create reverse mapping of currency names to codes
    currency_map = get_currency_map()
    name_to_code = {}
    for code, name in currency_map.items():
        # Add full name mapping
        name_to_code[name.upper()] = code
        # Add individual words from the name for partial matching
        for word in name.upper().split():
            if word not in ['AND', 'OF', 'NEW']:  # Skip common words
                name_to_code[word] = code
    
    # Check for currency codes (e.g., USD, EUR)
    codes = re.findall(r'\b[A-Z]{3}\b', query_upper)
    currencies.extend([code for code in codes if code in valid_currencies])
    
    if len(currencies) >= 2:
        return currencies[:2]
        
    # Check for currency symbols
    symbols = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
    for symbol, code in symbols.items():
        if symbol in query and code in valid_currencies and code not in currencies:
            currencies.append(code)
            
    if len(currencies) >= 2:
        return currencies[:2]
    
    # Check for full currency names and their variations
    query_words = query_upper.split()
    i = 0
    while i < len(query_words):
        # Try multi-word combinations
        for j in range(min(5, len(query_words) - i), 0, -1):
            phrase = " ".join(query_words[i:i+j])
            if phrase in name_to_code:
                code = name_to_code[phrase]
                if code in valid_currencies and code not in currencies:
                    currencies.append(code)
                    i += j - 1
                    break
        i += 1
                    
        if len(currencies) >= 2:
            return currencies[:2]
            
    # Check for individual words that might be currency names
    for word in query_words:
        if word in name_to_code:
            code = name_to_code[word]
            if code in valid_currencies and code not in currencies:
                currencies.append(code)
                
        if len(currencies) >= 2:
            return currencies[:2]
    
    return currencies[:2] if len(currencies) >= 2 else []

def is_exchange_rate_query(query):
    """Check if query is about exchange rates"""
    query_lower = query.lower()
    
    # Check for exchange rate keywords
    keywords = ['exchange rate', 'currency conversion', 'convert currency', 'forex rate', 'fx rate', 'convert']
    if not any(keyword in query_lower for keyword in keywords):
        return False
        
    # Get valid currencies from API
    rates = get_exchange_rates()
    if not rates:
        return False
        
    # Find currencies in query
    currencies = find_currencies_in_query(query, rates.keys())
    return len(currencies) >= 2

def get_exchange_rate_data(query):
    """Get exchange rate data from query"""
    try:
        rates = get_exchange_rates()
        if not rates:
            return "Could you please clarify what you mean? I'll be able to help you better with a little more detail or call Customer support at +91-9876543210"
            
        currencies = find_currencies_in_query(query, rates.keys())
        if len(currencies) < 2:
            return "Could you please clarify which currencies you'd like to convert between?"
            
        from_curr, to_curr = currencies[:2]
        
        # Calculate rate through USD
        if from_curr == "USD":
            rate = rates[to_curr]
        else:
            rate = rates[to_curr] / rates[from_curr]
            
        return f"The current exchange rate from {from_curr} to {to_curr} is {rate:.4f}."
            
    except Exception as e:
        print(f"[ERROR] Exchange rate calculation failed: {e}")
        return "Could you please clarify what you mean? I'll be able to help you better with a little more detail or call Customer support at +91-9876543210"
