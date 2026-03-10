import streamlit as st
import requests

# 1. Configurazione di base
BASE_URL = "https://api.polygon.io"

# 2. Struttura Dati Razionale (Non la tua lista cruda)
# Devi usare i placeholder {} per capire quali input servono dinamicamente.
ENDPOINTS = {
    "Stocks - Last Trade": {"url": "/v2/last/trade/{ticker}", "inputs": ["ticker"]},
    "Stocks - Daily Open / Close": {"url": "/v1/open-close/{ticker}/{date}", "inputs": ["ticker", "date"]},
    "Forex - Previous Close": {"url": "/v2/aggs/ticker/C:{ticker}/prev", "inputs": ["ticker"]},
    "Reference - Market Status": {"url": "/v1/marketstatus/now", "inputs": []}
}

st.title("API Data Explorer (Polygon.io)")

# 3. Gestione Sicura della Chiave (Mai hardcodata)
api_key = st.text_input("Inserisci API Key", type="password")

if api_key:
    # 4. Selezione Dinamica
    selected_endpoint = st.selectbox("Seleziona Endpoint", list(ENDPOINTS.keys()))
    config = ENDPOINTS[selected_endpoint]
    
    # 5. Generazione Dinamica degli Input in base alle reali necessità dell'endpoint
    user_inputs = {}
    for req_input in config["inputs"]:
        if req_input == "date":
            user_inputs[req_input] = st.date_input("Seleziona Data").strftime("%Y-%m-%d")
        else:
            user_inputs[req_input] = st.text_input(f"Inserisci {req_input.capitalize()} (es. AAPL o EURUSD)").upper()
    
    if st.button("Esegui Richiesta"):
        # Costruzione URL e chiamata
        try:
            formatted_path = config["url"].format(**user_inputs)
            full_url = f"{BASE_URL}{formatted_path}?apiKey={api_key}"
            
            response = requests.get(full_url)
            
            if response.status_code == 200:
                st.success("Richiesta completata")
                st.json(response.json())
            else:
                st.error(f"Errore {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Errore di configurazione: {e}")
else:
    st.warning("Inserisci una API key per iniziare.")